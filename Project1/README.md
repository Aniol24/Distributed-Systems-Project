# Distributed Systems Project

This project simulates a simple **distributed system** with a central **Master server**
that coordinates access to a **shared variable** between multiple **WRClient** processes.

Each client can either:
- **Read-only (`r`)**: periodically read the shared value.
- **Read-Write (`rw`)**: request a lock, update the shared value, and release it.

---

## Architecture

![Architecture Diagram](img/image.png)

The **Master** listens on a TCP port (`127.0.0.1:12345`) and coordinates access using
a lock system (mutual exclusion).  
It processes messages (`Msg`) from clients defined in `Message.h`.

---

## 📂 Project Structure

```
.
├── Client/
│   ├── Wrclient.cpp
│   └── Wrclient.h
├── Master/
│   ├── Master.cpp
│   └── Master.h
├── Message/
│   ├── Message.cpp
│   └── Message.h
├── main.cpp
├── Makefile
└── README.md
```

---

## Build Instructions

Make sure you have **g++** (C++17 or later) installed.

```bash
make
```

This will build the executable:

```
program.exe
```

### Clean up object files and binaries:
```bash
make clean       # removes .o files
make fclean      # removes .o + program.exe
make re          # rebuilds everything from scratch
```

---

## How to Run

### 1️. Start the Master (server)
```bash
./program.exe server 12345
```

You should see:
```
[master] Listening on 127.0.0.1:12345
```

### 2️. Start one or more Clients
In another terminal:

#### Read-only client
```bash
./program.exe client 127.0.0.1 12345 r
```

#### Read/Write client
```bash
./program.exe client 127.0.0.1 12345 rw
```

Each client connects to the Master, sends requests, and logs actions:
```
[client] Connected to server
[client] Requested LOCK
[client] Received LOCK_OK
[client] Updated shared value to 43
[client] Released lock
```

---

## Communication Protocol

Defined in `Message.h` as enum `Msg`:
- `READ_REQ` / `READ_RESP`
- `UPDATE_REQ` / `UPDATE_OK`
- `LOCK_REQ` / `LOCK_OK` / `LOCK_REL`
- `ERR`

The Master enforces **mutual exclusion**: only one writer at a time.  
If a client disconnects while holding the lock, the Master automatically grants it to the next in queue.

---

## Requirements
- **C++17** or newer
- Works on Linux, macOS, or WSL (Windows Subsystem for Linux)

---

## Authors
- **Aniol Vergés** 
- **Aleix Batchelli** 

---

## License
MIT License — Free to use, modify, and distribute for educational purposes.
