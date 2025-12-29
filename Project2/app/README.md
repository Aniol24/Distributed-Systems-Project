# Distributed Mutual Exclusion Project

## 📖 Overview
This project implements a distributed application with **two heavyweight processes** (ProcessA and ProcessB), each managing **three lightweight processes**.  
All processes run on the same machine but communicate **only via sockets**.  
The goal is to explore **distributed mutual exclusion algorithms** and **logical clocks**.

---

## 🎯 Objectives
- Implement **Lamport clocks** and use them in mutual exclusion.
- Apply **token-based mutual exclusion** between heavyweight processes.
- Apply **Lamport’s algorithm** among ProcessA’s lightweight processes.
- Apply **Ricart–Agrawala’s algorithm** among ProcessB’s lightweight processes.
- Demonstrate synchronization and correct access to a shared resource (the screen).

---

## ⚙️ Architecture

### Heavyweight Processes
- **ProcessA**
  - Manages: `ProcessLWA1`, `ProcessLWA2`, `ProcessLWA3`
  - Coordinates lightweights using **Lamport’s mutual exclusion**
- **ProcessB**
  - Manages: `ProcessLWB1`, `ProcessLWB2`, `ProcessLWB3`
  - Coordinates lightweights using **Ricart–Agrawala’s mutual exclusion**

### Lightweight Processes
- Infinite loop:
  1. Wait for heavyweight permission (`CS_GRANT`)
  2. Request critical section (via Lamport or Ricart–Agrawala)
  3. Print ID **10 times**, waiting **1 second** each time
  4. Release critical section
  5. Notify heavyweight (`DONE`)

### Communication
- **Sockets (TCP)** for all inter-process communication
- **Message format (JSON)**:
  ```json
  {
    "type": "REQUEST | REPLY | RELEASE | TOKEN | CS_GRANT | DONE",
    "sender": "A1 | B2 | A | B",
    "ts": 12,
    "payload": {}
  }

## 🔑 Mutual Exclusion

### Heavyweight ↔ Heavyweight
- **Token-based mutual exclusion**
- Only the heavyweight holding the token can coordinate its lightweights
- After all lightweights finish, the token is passed to the other heavyweight

### ProcessA’s Lightweights
- **Lamport’s algorithm**
- Each lightweight maintains a Lamport clock
- Requests are queued by `(timestamp, process_id)`
- Enter CS when:
  - All REPLYs received
  - Own request is at the head of the queue

### ProcessB’s Lightweights
- **Ricart–Agrawala’s algorithm**
- Each lightweight broadcasts REQUEST with timestamp
- Replies immediately unless:
  - Already requesting CS with smaller `(ts, id)`
  - Currently in CS
- Deferred replies sent after releasing CS

---

## ⚙️ Implementation Details

### Logical Clocks
- **LamportClock class** with methods:
  - `tick()` → local event
  - `send()` → before sending a message
  - `recv(ts)` → on receiving a message

### Lightweight Skeleton
```python
while True:
    wait_for_heavyweight()
    request_cs()
    for i in range(10):
        print(f"I'm lightweight process {myID}")
        time.sleep(1)
    release_cs()
    notify_heavyweight()
```

## 📡 Message Format

All communication between heavyweight and lightweight processes uses **JSON over TCP sockets**.  
Each message follows a consistent schema:

```json
{
  "type": "REQUEST | REPLY | RELEASE | TOKEN | CS_GRANT | DONE",
  "sender": "A | B | A1 | A2 | A3 | B1 | B2 | B3",
  "ts": 12,
  "payload": {}
}
```



