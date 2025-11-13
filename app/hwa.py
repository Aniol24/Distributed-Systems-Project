# hwa.py
import sys
import socket
import threading
import time

def send_to_screen(message, host="127.0.0.1", port=6000):
    """Send a debug message to the screen server."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        # Send message followed by newline so screen_server can read a line
        s.sendall((message + "\n").encode("utf-8"))
    finally:
        s.close()

def light_weight_process(id: str, port: int, peer_ports: list):
    """Worker function executed by a single thread."""
    send_to_screen(f"[{id}] started on port {port} with peers {peer_ports}")
    try:
        pass
        # Example lightweight loop to simulate activity
        #for i in range(10):
        #    send_to_screen(f"[{id}] tick {i} on {port}; peers={peer_ports}")
        #    time.sleep(0.5)
    finally:
        send_to_screen(f"[{id}] exiting")

def start_server(listen_port, host="127.0.0.1"):
    
    # --- start three threads of light_weight_process ---
    peer_ports = [listen_port + 1, listen_port + 2]  # example peer list
    t = [None] * 3
    t[0] = threading.Thread( target=light_weight_process, args=("LA1", 5101, [5102, 5103]), daemon=True)
    t[1] = threading.Thread( target=light_weight_process, args=("LA2", 5102, [5101, 5103]), daemon=True)
    t[2] = threading.Thread( target=light_weight_process, args=("LA3", 5103, [5101, 5102]), daemon=True)
    for i in range(3):
        t[i].start()
        #send_to_screen(f"[HWA] Started thread {i}")


    
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, listen_port))
    server_socket.listen()
    #send_to_screen(f"[HWA] Server started on {host}:{listen_port}")
    #send_to_screen("[HWA] Waiting for a connection...")

    while True:
        conn, addr = server_socket.accept()
        #send_to_screen(f"[HWA] Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                msg = data.decode("utf-8")
                #send_to_screen(f"[HWA] Received: {msg}")
                conn.sendall(b"Message received")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <listen_port>")
        sys.exit(1)

    listen_port = int(sys.argv[1])
    start_server(listen_port)
