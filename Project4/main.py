import sys
import argparse
import time
import multiprocessing
from NodeUtilities import *

REGISTRY = {
    "A1": 5001, "A2": 5002, "A3": 5003,
    "B1": 6001, "B2": 6002,
    "C1": 7001, "C2": 7002
}

TOPOLOGY = {
    "A1": ["A2", "A3"],
    "A2": ["A1", "A3", "B1"],
    "A3": ["A1", "A2", "B2"],
    "B1": [],
    "B2": ["C1", "C2"],
    "C1": [],
    "C2": []
}

def get_neighbors(node_id):
    neighbor_ids = TOPOLOGY[node_id]
    neighbor_map = {}
    for n_id in neighbor_ids:
        if n_id in REGISTRY:
            neighbor_map[n_id] = REGISTRY[n_id]
    return neighbor_map

def start_node_process(node_id):
    my_port = REGISTRY[node_id]
    neighbors = get_neighbors(node_id)
    
    time.sleep(0.5) 
    
    print(f"[*] Launching {node_id} on port {my_port}")

    try:
        node_instance = None
        if node_id.startswith("A"):
            node_instance = CoreNode(node_id, my_port, neighbors)
        elif node_id.startswith("B"):
            node_instance = Layer1Node(node_id, my_port, neighbors)
        elif node_id.startswith("C"):
            node_instance = Layer2Node(node_id, my_port, neighbors)

        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[!] Error in {node_id}: {e}")

def launch_all_nodes():
    processes = []
    print("[-] Starting System (Press Ctrl+C to stop all nodes)...")
    
    for node_id in REGISTRY.keys():
        p = multiprocessing.Process(target=start_node_process, args=(node_id,))
        p.daemon = True 
        processes.append(p)
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down all nodes...")
        for p in processes:
            p.terminate()

def main():
    parser = argparse.ArgumentParser(description="Distributed System Launcher")
    parser.add_argument("node_id", nargs="?", type=str, help="ID of a specific node (e.g., A1)")
    parser.add_argument("--all", action="store_true", help="Launch the entire system")
    args = parser.parse_args()

    if args.all:
        launch_all_nodes()
    elif args.node_id:
        if args.node_id.upper() not in REGISTRY:
            print(f"Error: {args.node_id} is not a valid node.")
            return
        start_node_process(args.node_id.upper())
    else:
        print("Usage: python main.py <NODE_ID> OR python main.py --all")

if __name__ == "__main__":
    main()