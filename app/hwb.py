# hwa.py
import sys
import socket
import threading
import lwb
import hwa

has_token = False
listen_port = 0
ports = [5201, 5202, 5203]

def start_server(listen_port, host="127.0.0.1"):
    # --- start three LBmport processes as threads ---
    threads = []
    threads.append(threading.Thread(
        target=lwb.light_weight_process,
        args=("LB1", ports[0], {"LB2": ports[1], "LB3": ports[2]}, listen_port),
        daemon=False
    ))
    threads.append(threading.Thread(
        target=lwb.light_weight_process,
        args=("LB2", ports[1], {"LB1": ports[0], "LB3": ports[2]}, listen_port),
        daemon=False
    ))
    threads.append(threading.Thread(
        target=lwb.light_weight_process,
        args=("LB3", ports[2], {"LB1": ports[0], "LB2": ports[1]}, listen_port),
        daemon=False
    ))

    for t in threads:
        t.start()

    # allow LBmport processes to run
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

    ack = {"LB1": 0, "LB2": 0, "LB3": 0}

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
                            s.connect(("127.0.0.1", 5000))
                            s.sendall(b"TOKEN\n")
                            ack = {key: 0 for key in ack}  # reset ack
                        except Exception:
                            pass
                
                if parts and parts[0] == "TOKEN":
                    lwb.send_to_screen(f"[HWA] Received TOKEN, allowing Lamport processes to run")
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
