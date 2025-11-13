# hwa.py
import sys
import socket
import threading
import lwa


def start_server(listen_port, host="127.0.0.1"):
    # --- start three threads of light_weight_process ---
    t = [None] * 3
    t[0] = threading.Thread( target=lwa.light_weight_process, args=("LA1", 5101, [5102, 5103]), daemon=True)
    t[1] = threading.Thread( target=lwa.light_weight_process, args=("LA2", 5102, [5101, 5103]), daemon=True)
    t[2] = threading.Thread( target=lwa.light_weight_process, args=("LA3", 5103, [5101, 5102]), daemon=True)
    for i in range(3):
        t[i].start()
        #send_to_screen(f"[HWA] Started thread {i}")

    lwa.can_run = True 

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
