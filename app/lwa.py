import socket
import threading
import time

can_run = False
has_token = True

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

class LamportMutex:
    def __init__(self, pid, peers):
        self.pid = pid
        self.clock = 0
        self.queue = []  # list of (ts, pid)
        self.replies = set()
        self.peers = peers
        self.lock = threading.Lock()

    def tick(self, other_ts=None):
        with self.lock:
            if other_ts is not None:
                self.clock = max(self.clock, other_ts)
            self.clock += 1
            return self.clock

    def request_cs(self):
        ts = self.tick()
        self.queue.append((ts, self.pid))
        self.broadcast(f"REQUEST {ts} {self.pid}")
        self.replies.clear()

    def release_cs(self):
        ts = self.tick()
        self.broadcast(f"RELEASE {ts} {self.pid}")
        self.queue = [(t,i) for (t,i) in self.queue if i != self.pid]

    def broadcast(self, msg):
        for peer_port in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", peer_port))
                s.sendall((msg+"\n").encode("utf-8"))
                s.close()
            except Exception:
                pass

    def can_enter(self):
        self.queue.sort()
        return self.queue and self.queue[0][1] == self.pid and len(self.replies) == len(self.peers)

def listener(server_socket, mutex):
    while True:
        conn, addr = server_socket.accept()
        data = conn.recv(1024).decode("utf-8").strip()
        if not data:
            conn.close()
            continue

        parts = data.split()
        if parts[0] == "REQUEST":
            ts, pid = int(parts[1]), parts[2]
            mutex.tick(ts)
            mutex.queue.append((ts, pid))
            # reply back
            reply = f"REPLY {mutex.tick()} {mutex.pid}"
            conn.sendall(reply.encode("utf-8"))

        elif parts[0] == "REPLY":
            ts, pid = int(parts[1]), parts[2]
            mutex.tick(ts)
            mutex.replies.add(pid)

        elif parts[0] == "RELEASE":
            ts, pid = int(parts[1]), parts[2]
            mutex.tick(ts)
            mutex.queue = [(t,i) for (t,i) in mutex.queue if i != pid]

        conn.close()

def light_weight_process(id: str, port: int, peer_ports: list):
    global can_run, has_token

    # Start server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()
    send_to_screen(f"[{id}] listening on 127.0.0.1:{port}")

    mutex = LamportMutex(id, peer_ports)

    # Launch listener thread
    threading.Thread(target=listener, args=(server_socket, mutex), daemon=True).start()

    # Wait until can_run is True
    while not can_run:
        time.sleep(0.1)

    # Main loop
    while can_run:
        #send_to_screen(f"[{id}] Trying to enter critical section")
        # Request critical section
        mutex.request_cs()
        while not mutex.can_enter():
            time.sleep(0.1)

        # --- Critical Section ---
        send_to_screen(f"[{id}] ENTER critical section")
        time.sleep(1)  # simulate work
        send_to_screen(f"[{id}] EXIT critical section")

        # Release
        mutex.release_cs()
        time.sleep(2)  # non-critical work
