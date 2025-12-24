import grpc
from concurrent import futures
import threading

import chat_pb2
import chat_pb2_grpc

FILE_NAME = "messages.txt"
lock = threading.Lock()

class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def SendMessage(self, request, context):
        line = f"{request.nickname}: {request.text}\n"
        with lock:
            with open(FILE_NAME, "a", encoding="utf-8") as f:
                f.write(line)
        return chat_pb2.Status(ok=True)

    def GetMessages(self, request, context):
        with lock:
            try:
                with open(FILE_NAME, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except FileNotFoundError:
                lines = []

        new_lines = lines[request.last_line:]
        return chat_pb2.Messages(lines=new_lines, new_last_line=len(lines))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🟢 Chat server running on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
