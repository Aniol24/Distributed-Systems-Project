# lightweight_a.py
import socket
import threading
import time
import json

# --- Helpers for message encoding/decoding ---
def encode(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")

def decode_line(line: bytes) -> dict:
    return json.loads(line.decode("utf-8"))

# --- Lamport Clock ---
class LamportClock:
    def __init__(self):
        self.c = 0
    def tick(self):
        self.c += 1
        return self.c
    def send(self):
        self.c += 1
        return self.c
    def recv(self, t):
        self.c = max(self.c, t) + 1
        return self.c
    def now(self):
        return self.c

# --- Lightweight Process A (Lamport mutual exclusion) ---
class LightweightA:
    def __init__(self, my_id, listen_port, hw_addr, peers):
        self.my_id = my_id
        self.listen_port = listen_port
        self.hw_addr = hw_addr  # heavyweight address (host, port)
        self.peers = peers      # list of (host, port) for A1, A2, A3
        self.clock = LamportClock()
        self.queue = []         # request queue [(ts, pid)]
        self.replies = set()
        self.running = True

    # --- Networking ---
    def _send(self, addr, msg):
        try:
            s = socket.create_connection(addr, timeout=2)
            s.sendall(encode(msg))
            s.close()
        except Exception as e:
            print(f"[{self.my_id}] Error sending to {addr}: {e}")

    def listen_loop(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("127.0.0.1", self.listen_port))
        srv.listen(8)
        print(f"[{self.my_id}] Listening on port {self.listen_port}")
        while self.running:
            c, _ = srv.accept()
            line = c.makefile("rb").readline()
            msg = decode_line(line)
            self.handle_message(msg)
            c.close()

    # --- Lamport mutual exclusion handlers ---
    def request_cs(self):
        ts = self.clock.send()
        req = {"type": "REQUEST", "sender": self.my_id, "ts": ts}
        self.queue.append((ts, self.my_id))
        self.replies.clear()
        for peer in self.peers:
            self._send(peer, req)

    def release_cs(self):
        ts = self.clock.tick()
        rel = {"type": "RELEASE", "sender": self.my_id, "ts": ts}
        # remove own request from queue
        self.queue = [(t,p) for (t,p) in self.queue if p != self.my_id]
        for peer in self.peers:
            self._send(peer, rel)

    def handle_message(self, msg):
        if msg["type"] == "REQUEST":
            self.clock.recv(msg["ts"])
            self.queue.append((msg["ts"], msg["sender"]))
            rep = {"type": "REPLY", "sender": self.my_id, "ts": self.clock.send()}
            # find peer addr
            for peer in self.peers:
                if peer[1] == int(msg["sender"][-1]) + 5100:  # simplistic mapping
                    self._send(peer, rep)
        elif msg["type"] == "REPLY":
            self.clock.recv(msg["ts"])
            self.replies.add(msg["sender"])
        elif msg["type"] == "RELEASE":
            self.clock.recv(msg["ts"])
            self.queue = [(t,p) for (t,p) in self.queue if p != msg["sender"]]

    def can_enter_cs(self):
        # Check if all replies received and own request is at queue head
        if len(self.replies) < len(self.peers):
            return False
        # Sort queue by (ts, pid)
        self.queue.sort()
        return self.queue and self.queue[0][1] == self.my_id
    
    def write_to_screen(msg):
        s = socket.create_connection(("127.0.0.1", 6000))
        s.sendall((msg + "\n").encode("utf-8"))
        s.close()

    # --- Main loop ---
    def run(self):
        threading.Thread(target=self.listen_loop, daemon=True).start()
        while True:
            # Wait for heavyweight CS_GRANT
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", self.listen_port+100))  # separate port for HW
            srv.listen(1)
            c, _ = srv.accept()
            line = c.makefile("rb").readline()
            msg = decode_line(line)
            c.close()
            if msg["type"] == "CS_GRANT":
                self.write_to_screen(f"[{self.my_id}] Received CS_GRANT from heavyweight")
                # Request CS among peers
                self.request_cs()
                # Wait until allowed
                while not self.can_enter_cs():
                    time.sleep(0.2)
                # Critical section: print 10 times
                for i in range(10):
                    print(f"I'm lightweight process {self.my_id}")
                    time.sleep(1)
                # Release CS
                self.release_cs()
                # Notify heavyweight
                self._send(self.hw_addr, {"type":"DONE","sender":self.my_id,"ts":self.clock.tick()})

if __name__ == "__main__":
    # Example config for A1
    my_id = "A1"
    listen_port = 5101
    hw_addr = ("127.0.0.1", 5000)  # heavyweight A
    peers = [("127.0.0.1", 5101), ("127.0.0.1", 5102), ("127.0.0.1", 5103)]
    lw = LightweightA(my_id, listen_port, hw_addr, peers)
    lw.run()
