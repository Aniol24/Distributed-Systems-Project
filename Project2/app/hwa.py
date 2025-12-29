# hwa.py
import sys
import socket
import threading
import lwa
import hwb

has_token = True
listen_port = 0
ports = [5101, 5102, 5103]

def start_server(listen_port, host="127.0.0.1"):
    # --- start three Lamport processes as threads ---
    threads = []
    threads.append(threading.Thread(
        target=lwa.light_weight_process,
        args=("LA1", ports[0], {"LA2": ports[1], "LA3": ports[2]}, listen_port),
        daemon=False
    ))
    threads.append(threading.Thread(
        target=lwa.light_weight_process,
        args=("LA2", ports[1], {"LA1": ports[0], "LA3": ports[2]}, listen_port),
        daemon=False
    ))
    threads.append(threading.Thread(
        target=lwa.light_weight_process,
        args=("LA3", ports[2], {"LA1": ports[0], "LA2": ports[1]}, listen_port),
        daemon=False
    ))

    for t in threads:
        t.start()

    # allow Lamport processes to run
    if has_token:
        for p in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(("127.0.0.1", p))
                s.sendall(b"TOKEN\n")
            except Exception:
                pass
            finally:
                try:
                    s.close()
                except Exception:
                    pass

    # control server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, listen_port))
    server_socket.listen()
    server_socket.settimeout(1.0)  # periodic wakeup

    ack = {"LA1": 0, "LA2": 0, "LA3": 0}

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("Interrupted, shutting down")
                break

            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                msg = data.decode("utf-8").strip()
                parts = msg.split()
                if parts and parts[0] == "DONE":
                    pid = parts[1]
                    ack[pid] = 1
                    count = sum(ack.values())
                    if count == 3:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            s.connect(("127.0.0.1", 4000))
                            s.sendall(b"TOKEN\n")
                            ack = {key: 0 for key in ack}  # reset ack
                        except Exception:
                            pass
                
                if parts and parts[0] == "TOKEN":
                    lwa.send_to_screen(f"[HWA] Received TOKEN, allowing Lamport processes to run")
                    for p in ports:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        try:
                            s.connect(("127.0.0.1", p))
                            s.sendall(b"TOKEN\n")
                        except Exception:
                            pass
    finally:
        try:
            server_socket.close()
        except Exception:
            pass
        for t in threads:
            try:
                t.join(timeout=1.0)
            except Exception:
                pass
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <listen_port>")
        sys.exit(1)

    listen_port = int(sys.argv[1])
    start_server(listen_port)
