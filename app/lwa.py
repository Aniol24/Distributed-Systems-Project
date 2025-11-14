import socket
import threading
import time
import sys
import random

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
        self.clock = random.randint(0, 3)
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
        # enqueue our own request
        self.queue.append((ts, self.pid))
        self.replies.clear()
        self.broadcast(f"REQUEST {ts} {self.pid}")

    def release_cs(self):
        ts = self.tick()
        self.broadcast(f"RELEASE {ts} {self.pid}")
        # remove our own request
        self.queue = [(t, i) for (t, i) in self.queue if i != self.pid]

    def broadcast(self, msg):
        for peer_port in self.peers.values():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("127.0.0.1", peer_port))
                s.sendall((msg + "\n").encode("utf-8"))
                s.close()
            except Exception:
                pass

    def can_enter(self):
        # sort by (timestamp, pid) for deterministic order
        self.queue.sort()
        return (
            len(self.queue) > 0
            and self.queue[0][1] == self.pid
            and len(self.replies) == len(self.peers)
        )

def listener(server_socket, mutex):
    server_socket.settimeout(1.0)  # periodic wakeup
    try:
        while True:
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue

            data = conn.recv(1024).decode("utf-8").strip()
            if not data:
                conn.close()
                continue

            parts = data.split()
            if parts[0] == "REQUEST":
                #send_to_screen(f"[{mutex.pid}] Received REQUEST from {parts[2]}")
                ts, pid = int(parts[1]), parts[2]
                mutex.tick(ts)
                # store sender’s timestamp for consistency
                mutex.queue.append((ts, pid))
                reply = f"REPLY {mutex.tick()} {mutex.pid}"
                
                #send_to_screen(f"[{mutex.pid}] Sending REPLY to {pid} with port {mutex.peers[pid]}")
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect(("127.0.0.1", mutex.peers[pid]))
                    reply = f"REPLY {mutex.tick()} {mutex.pid}"
                    s.sendall((reply + "\n").encode("utf-8"))
                    
                except Exception:
                    pass

            elif parts[0] == "REPLY":
                #send_to_screen(f"[{mutex.pid}] Received REPLY from {parts[2]}")
                ts, pid = int(parts[1]), parts[2]
                mutex.tick(ts)
                mutex.replies.add(pid)
                #send_to_screen(f"[{mutex.pid}] Received REPLY from {pid}")

            elif parts[0] == "RELEASE":
                ts, pid = int(parts[1]), parts[2]
                mutex.tick(ts)
                mutex.queue = [(t, i) for (t, i) in mutex.queue if i != pid]

            elif parts[0] == "TOKEN":
                global can_run
                can_run = True

            try:
                conn.close()
            except Exception:
                pass
    except KeyboardInterrupt:
        print(f"[{mutex.pid}] Listener shutting down")
        try:
            server_socket.close()
        except Exception:
            pass
        sys.exit(0)

def light_weight_process(id: str, port: int, peer_ports: dict, hw_port):
    global can_run

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", port))
    server_socket.listen()
    send_to_screen(f"[{id}] listening on 127.0.0.1:{port}")

    mutex = LamportMutex(id, peer_ports)

    # Launch listener thread (non-daemon for clean shutdown)
    listener_thread = threading.Thread(target=listener, args=(server_socket, mutex), daemon=False)
    listener_thread.start()

    
    try:
        while True:
            while not can_run:
                time.sleep(0.1)
            # Do 10 CS entries
            for _ in range(10):
                time.sleep(random.uniform(0, 3))
                mutex.request_cs()
                while not mutex.can_enter():
                    time.sleep(0.05)

                send_to_screen(f"I am light weight process [{id}] entering critical section.")
                time.sleep(1)
                mutex.release_cs()

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", hw_port))
            s.sendall(f"DONE {id}\n".encode("utf-8"))
            can_run = False
    
    except KeyboardInterrupt:
        print(f"[{id}] Interrupted, shutting down")
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
        

            
    
