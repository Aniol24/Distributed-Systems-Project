import socket
import threading
import time
import sys
import random

can_run = False  # external start gate

def send_to_screen(message, host="127.0.0.1", port=6000):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall((message + "\n").encode("utf-8"))
    except Exception:
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass

def sorted_ids(peer_ports):
    """Stable, deterministic order of process IDs."""
    return sorted(peer_ports.keys())

class VectorClock:
    def __init__(self, ids, self_id):
        self.ids = ids               # ordered list of all IDs
        self.index = {pid: i for i, pid in enumerate(ids)}
        self.v = [0] * len(ids)
        self.self_id = self_id
        self.lock = threading.Lock()

    def tick(self):
        with self.lock:
            self.v[self.index[self.self_id]] += 1
            return list(self.v)

    def merge_and_tick(self, other_v):
        with self.lock:
            for i in range(len(self.v)):
                self.v[i] = max(self.v[i], other_v[i])
            self.v[self.index[self.self_id]] += 1
            return list(self.v)

    def snapshot(self):
        with self.lock:
            return list(self.v)

    @staticmethod
    def happens_before(a, b):
        """Return True iff a -> b (a happens-before b)."""
        leq = True
        strict = False
        for i in range(len(a)):
            if a[i] > b[i]:
                leq = False
                break
            if a[i] < b[i]:
                strict = True
        return leq and strict

class RicartAgrawalaMutex:
    def __init__(self, pid, peers):
        """
        pid: this process id (string)
        peers: dict pid -> port
        """
        self.pid = pid
        self.peers = peers
        self.all_ids = sorted_ids(peers | {pid: None})  # include self
        self.vc = VectorClock(self.all_ids, pid)
        self.requesting = False
        self.request_vc = None   # vector clock at request time
        self.replies = set()     # pids that replied
        self.deferred = set()    # pids to whom we owe a reply
        self.lock = threading.Lock()

    def broadcast(self, msg):
        for peer_id, peer_port in self.peers.items():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", peer_port))
                s.sendall((msg + "\n").encode("utf-8"))
                s.close()
            except Exception:
                pass

    def send_reply(self, to_pid):
        port = self.peers.get(to_pid)
        if port is None:
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", port))
            # include current vector clock
            vc = self.vc.tick()
            payload = f"REPLY {to_pid} {self.pid} {' '.join(map(str, vc))}"
            s.sendall((payload + "\n").encode("utf-8"))
            s.close()
        except Exception:
            pass

    def request_cs(self):
        with self.lock:
            self.requesting = True
            self.replies.clear()
            # take a vector clock snapshot after local tick
            req_vc = self.vc.tick()
            self.request_vc = req_vc

        # broadcast REQUEST with vector clock
        payload = f"REQUEST {self.pid} {' '.join(map(str, req_vc))}"
        self.broadcast(payload)

    def can_enter(self):
        with self.lock:
            return self.requesting and len(self.replies) == len(self.peers)

    def release_cs(self):
        # after CS, send deferred replies
        to_reply = []
        with self.lock:
            self.requesting = False
            to_reply = list(self.deferred)
            self.deferred.clear()
            self.request_vc = None
            self.vc.tick()  # logical progress
        for pid in to_reply:
            self.send_reply(pid)

    def handle_request(self, from_pid, from_vc):
        """
        Decide whether to REPLY immediately or defer, according to RA + vector clocks.
        Priority rule:
          - If from_vc happens-before our request_vc: peer has priority -> REPLY.
          - If our request_vc happens-before from_vc: we have priority -> defer.
          - If concurrent: tie-break by pid (smaller pid wins).
        If not currently requesting, REPLY immediately.
        """
        with self.lock:
            # merge their clock, tick locally
            self.vc.merge_and_tick(from_vc)

            if not self.requesting or self.request_vc is None:
                # not competing -> reply immediately
                immediate = True
            else:
                a = from_vc
                b = self.request_vc
                if VectorClock.happens_before(a, b):
                    immediate = True
                elif VectorClock.happens_before(b, a):
                    immediate = False
                else:
                    # concurrent: pid tie-break (string compare ensures deterministic order)
                    immediate = (from_pid < self.pid)

            if immediate:
                pass
            else:
                self.deferred.add(from_pid)

        if immediate:
            self.send_reply(from_pid)

    def handle_reply(self, from_pid, from_vc):
        with self.lock:
            self.vc.merge_and_tick(from_vc)
            self.replies.add(from_pid)

def listener(server_socket, mutex: RicartAgrawalaMutex):
    server_socket.settimeout(1.0)
    try:
        while True:
            try:
                conn, _ = server_socket.accept()
            except socket.timeout:
                continue

            try:
                data = conn.recv(2048).decode("utf-8").strip()
            except Exception:
                data = ""
            if not data:
                try:
                    conn.close()
                except Exception:
                    pass
                continue

            parts = data.split()
            # Protocol:
            # REQUEST <from_pid> <vc...>
            # REPLY   <to_pid> <from_pid> <vc...>
            try:
                if parts[0] == "REQUEST":
                    from_pid = parts[1]
                    from_vc = list(map(int, parts[2:]))
                    mutex.handle_request(from_pid, from_vc)

                elif parts[0] == "REPLY":
                    to_pid = parts[1]
                    from_pid = parts[2]
                    if to_pid == mutex.pid:
                        from_vc = list(map(int, parts[3:]))
                        mutex.handle_reply(from_pid, from_vc)

                elif parts[0] == "TOKEN":
                    # external start signal
                    global can_run
                    can_run = True
            except Exception:
                # robust to malformed input
                pass

            try:
                conn.close()
            except Exception:
                pass
    except KeyboardInterrupt:
        try:
            server_socket.close()
        except Exception:
            pass
        sys.exit(0)

def light_weight_process(id: str, port: int, peer_ports: dict, hw_port):
    global can_run

    # include self in ID universe
    peer_ports = dict(peer_ports)  # shallow copy
    if id in peer_ports:
        # ensure no conflict
        del peer_ports[id]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()
    send_to_screen(f"[{id}] listening on 127.0.0.1:{port}")

    mutex = RicartAgrawalaMutex(id, peer_ports)

    listener_thread = threading.Thread(target=listener, args=(server_socket, mutex), daemon=False)
    listener_thread.start()

    try:
        while True:
            while not can_run:
                time.sleep(0.1)

            # perform 10 CS entries
            for _ in range(10):
                time.sleep(random.uniform(0, 3))
                mutex.request_cs()
                while not mutex.can_enter():
                    time.sleep(0.05)

                send_to_screen(f"I am light weight process [{id}] entering critical section.")
                time.sleep(1)

                mutex.release_cs()

            # notify completion
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", hw_port))
                s.sendall(f"DONE {id}\n".encode("utf-8"))
                s.close()
            except Exception:
                pass

            can_run = False

    except KeyboardInterrupt:
        pass
    finally:
        try:
            server_socket.close()
        except Exception:
            pass
        try:
            listener_thread.join(timeout=1.0)
        except Exception:
            pass
        sys.exit(0)
