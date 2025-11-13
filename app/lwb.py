# lightweight_b.py
import socket
import threading
import time
import json
import sys

# --- Helpers for message encoding/decoding ---
def encode(msg: dict) -> bytes:
    return (json.dumps(msg) + "\n").encode("utf-8")

def decode_line(line: bytes) -> dict:
    return json.loads(line.decode("utf-8"))

# --- Lamport Clock (used for timestamps) ---
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

# --- Lightweight Process B (Ricart–Agrawala mutual exclusion) ---
class LightweightB:
    def __init__(self, my_id, listen_port, hw_addr, peers):
        self.my_id = my_id
        self.listen_port = listen_port
        self.hw_addr = hw_addr  # heavyweight address (host, port)
        self.peers = peers      # list of (id, port) for B1, B2, B3
        self.clock = LamportClock()
        self.request_ts = None
        self.deferred = set()   # set of (peer_id, ts)
        self.waiting = set()    # set of (peer_id, port)
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
            try:
                line = c.makefile("rb").readline()
                if not line:
                    c.close()
                    continue
                msg = decode_line(line)
                self.handle_message(msg)
            finally:
                c.close()

    # --- Ricart–Agrawala handlers ---
    def request_cs(self):
        ts = self.clock.send()
        self.request_ts = ts
        self.waiting = {peer for peer in self.peers if peer[0] != self.my_id}
        req = {"type": "REQUEST", "sender": self.my_id, "ts": ts}
        for peer in self.peers:
            if peer[0] != self.my_id:  # don't send to self
                self._send(("127.0.0.1", peer[1]), req)

    def release_cs(self):
        self.clock.tick()
        # Send REPLY to all deferred peers
        for peer_id, _ts in list(self.deferred):
            rep = {"type": "REPLY", "sender": self.my_id, "ts": self.clock.send()}
            for peer in self.peers:
                if peer[0] == peer_id:
                    self._send(("127.0.0.1", peer[1]), rep)
                    break
        self.deferred.clear()
        self.request_ts = None

    def handle_message(self, msg):
        mtype = msg.get("type")
        if mtype == "REQUEST":
            self.clock.recv(msg["ts"])
            tsj, sender = msg["ts"], msg["sender"]
            # If I am not requesting or my request has lower priority, reply immediately
            if self.request_ts is None or (self.request_ts, self.my_id) > (tsj, sender):
                rep = {"type": "REPLY", "sender": self.my_id, "ts": self.clock.send()}
                for peer in self.peers:
                    if peer[0] == sender:
                        self._send(("127.0.0.1", peer[1]), rep)
                        break
            else:
                # Defer reply
                self.deferred.add((sender, tsj))

        elif mtype == "REPLY":
            self.clock.recv(msg["ts"])
            # Mark peer as replied
            self.waiting = {peer for peer in self.waiting if peer[0] != msg["sender"]}

        elif mtype == "RELEASE":
            # Optional: not strictly needed in Ricart–Agrawala for reply bookkeeping
            self.clock.recv(msg["ts"])

        elif mtype == "CS_GRANT":
            # Heavyweight says our group can print; run CS sequence in a separate thread
            threading.Thread(target=self._on_cs_grant, daemon=True).start()

    def can_enter_cs(self):
        return len(self.waiting) == 0 and self.request_ts is not None

    def write_to_screen(self, msg):
        try:
            s = socket.create_connection(("127.0.0.1", 6000), timeout=2)
            s.sendall((msg + "\n").encode("utf-8"))
            s.close()
        except Exception as e:
            print(f"[{self.my_id}] Error writing to screen: {e}")

    # --- Sequence triggered by CS_GRANT ---
    def _on_cs_grant(self):
        print(f"[{self.my_id}] Received CS_GRANT from heavyweight")
        # Request CS among peers
        self.request_cs()
        # Wait until allowed
        while not self.can_enter_cs():
            time.sleep(0.2)
        # Critical section: print 10 times
        for _ in range(10):
            self.write_to_screen(f"I'm lightweight process {self.my_id}")
            time.sleep(1)
        # Release CS and notify heavyweight
        self.release_cs()
        self._send(self.hw_addr, {"type": "DONE", "sender": self.my_id, "ts": self.clock.tick()})

    # --- Main loop ---
    def run(self):
        # Start listener (handles REQUEST/REPLY/CS_GRANT)
        threading.Thread(target=self.listen_loop, daemon=True).start()
        # Keep the process alive
        while True:
            time.sleep(1)

# --- Entry point with arguments ---
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python lightweight_b.py <ID> <PORT>")
        sys.exit(1)

    my_id = sys.argv[1]             # e.g. "B1"
    listen_port = int(sys.argv[2])  # e.g. 5201
    hw_addr = ("127.0.0.1", 5001)   # heavyweight B

    # Define peers statically for B group
    peers = [("B1", 5201), ("B2", 5202), ("B3", 5203)]

    lw = LightweightB(my_id, listen_port, hw_addr, peers)
    lw.run()
