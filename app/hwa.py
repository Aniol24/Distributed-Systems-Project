# hwa.py
import sys
import socket
import threading
import lwa

def start_server(listen_port, host="127.0.0.1"):
    # --- start three Lamport processes as threads ---
    threads = []
    threads.append(threading.Thread(target=lwa.light_weight_process,
                                    args=("LA1", 5101, {"LA2": 5102, "LA3": 5103}),
                                    daemon=False))
    threads.append(threading.Thread(target=lwa.light_weight_process,
                                    args=("LA2", 5102, {"LA1": 5101, "LA3": 5103}),
                                    daemon=False))
    threads.append(threading.Thread(target=lwa.light_weight_process,
                                    args=("LA3", 5103, {"LA1": 5101, "LA2": 5102}),
                                    daemon=False))

    for t in threads:
        t.start()

    # allow Lamport processes to run
    lwa.can_run = True

    # control server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, listen_port))
    server_socket.listen()
    server_socket.settimeout(1.0)  # periodic wakeup

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue  # loop back, allows KeyboardInterrupt to be raised
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    msg = data.decode("utf-8")
                    conn.sendall(b"Message received")
    except KeyboardInterrupt:
        print("Interrupted, shutting down")
    finally:
        try:
            server_socket.close()
        except Exception:
            pass
        # join worker threads to exit cleanly
        for t in threads:
            t.join(timeout=1.0)
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <listen_port>")
        sys.exit(1)

    listen_port = int(sys.argv[1])
    start_server(listen_port)
