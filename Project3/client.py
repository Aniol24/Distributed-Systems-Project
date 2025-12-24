import grpc
import sys
import threading
import time
import curses

import chat_pb2
import chat_pb2_grpc

PROMPT = "tu mensaje: "

messages = []
last_line = 0
typed = ""
dirty = True
lock = threading.Lock()


def poll_messages(stub):
    global last_line, dirty, messages

    while True:
        try:
            resp = stub.GetMessages(chat_pb2.GetRequest(last_line=last_line))
            if resp.lines:
                with lock:
                    for line in resp.lines:
                        messages.append(line.strip())
                    last_line = resp.new_last_line
                    dirty = True
        except Exception:
            with lock:
                messages.append("[system] conexión perdida…")
                dirty = True

        time.sleep(1)


def draw(stdscr):
    global dirty, typed, messages

    stdscr.nodelay(True)
    curses.curs_set(1)

    while True:
        if dirty:
            with lock:
                stdscr.erase()
                h, w = stdscr.getmaxyx()

                msg_h = h - 2
                start = max(0, len(messages) - msg_h)

                y = 0
                for m in messages[start:]:
                    stdscr.addnstr(y, 0, m, w - 1)
                    y += 1

                stdscr.hline(h - 2, 0, "-", w - 1)
                stdscr.addnstr(h - 1, 0, PROMPT + typed, w - 1)

                cursor_x = min(len(PROMPT) + len(typed), w - 1)
                stdscr.move(h - 1, cursor_x)

                stdscr.refresh()
                dirty = False

        ch = stdscr.getch()
        if ch == -1:
            time.sleep(0.02)
            continue

        if ch in (10, 13):
            with lock:
                msg = typed.strip()
                typed = ""
                dirty = True
            if msg:
                yield msg
            continue

        if ch in (curses.KEY_BACKSPACE, 127, 8):
            with lock:
                typed = typed[:-1]
                dirty = True
            continue

        if ch == 27:
            return

        if 32 <= ch <= 126:
            with lock:
                typed += chr(ch)
                dirty = True


def ui_main(stub, nickname):
    global dirty, messages

    threading.Thread(target=poll_messages, args=(stub,), daemon=True).start()

    def curses_app(stdscr):
        global dirty

        with lock:
            messages.append(f"[system] Welcome {nickname}!")
            dirty = True

        for outgoing in draw(stdscr):
            try:
                stub.SendMessage(
                    chat_pb2.Message(nickname=nickname, text=outgoing)
                )
            except Exception:
                with lock:
                    messages.append("[system] no se pudo enviar")
                    dirty = True

    curses.wrapper(curses_app)


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <nickname>")
        sys.exit(1)

    server_ip = sys.argv[1]
    nickname = sys.argv[2]

    channel = grpc.insecure_channel(f"{server_ip}:50051")
    stub = chat_pb2_grpc.ChatServiceStub(channel)

    ui_main(stub, nickname)


if __name__ == "__main__":
    main()
