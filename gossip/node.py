# import socket
# import json
# import threading
# import time
# import uuid
# from typing import List
# import asyncio
# import websockets
#
#
# class GossipNode:
#     def __init__(self, host: str, port: int, peers: List[str] = None):
#         self.host = host
#         self.port = port
#         self.peers = peers if peers else []
#         self.messages = []
#         self.node_id = str(uuid.uuid4())
#         self.counter = 0
#         self.transaction_log = []
#         self.gossip_thread = threading.Thread(target=self._gossip)
#         self.gossip_thread.daemon = True
#
#     def start(self):
#         self._start_server()
#         self._start_gossip()
#
#     def _start_server(self):
#         server_thread = threading.Thread(target=self._server)
#         server_thread.daemon = True
#         server_thread.start()
#
#     # def _server(self):
#     #     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
#     #         server_socket.bind((self.host, self.port))
#     #         print(f"[*] GossipNode started on {self.host}:{self.port}")
#     #         while True:
#     #             client_socket, client_addr = server_socket.accept()
#     #             print(f"[*] Accepted connection from {client_addr}")
#     #
#     #             client_thread = threading.Thread(target=self._client_handler, args=(client_socket, client_addr))
#     #             client_thread.daemon = True
#     #             client_thread.start()
#     async def _server(self):
#         async with websockets.serve(self._client_handler, self.host, self.port):
#             print(f"[*] GossipNode started on {self.host}:{self.port}")
#             await asyncio.Future()  # Run the server indefinitely
#
#     def _handle_message(self, data: bytes, addr: tuple):
#         message = json.loads(data)
#         transaction_id = message["transaction_id"]
#
#         # Проверяем, есть ли транзакция в журнале
#         if not any(tx["transaction_id"] == transaction_id for tx in self.transaction_log):
#             print(f"[*] Received message from {addr}: {message['content']}")
#
#             self.transaction_log.append(message)
#             self.transaction_log.sort(key=lambda tx: tx["transaction_id"])
#
#             self._gossip(message)
#
#     def _start_gossip(self):
#         gossip_thread = threading.Thread(target=self._gossip_loop)
#         gossip_thread.daemon = True
#         gossip_thread.start()
#
#     def _gossip_loop(self):
#         while True:
#             for message in self.messages:
#                 self._gossip(message)
#             time.sleep(1)
#
#     def _gossip(self, message: dict):
#         for peer in self.peers:
#             host, port = peer
#             with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
#                 client_socket.sendto(json.dumps(message).encode("utf-8"), (host, int(port)))
#
#     def send_message(self, content: str):
#         self.counter += 1
#         transaction_id = f"{self.node_id}-{self.counter}"
#         message = {"transaction_id": transaction_id, "content": content}
#
#         self.transaction_log.append(message)
#         self._gossip(message)
#
#     async def _client_handler(self, websocket, path):
#         while True:
#             data = await websocket.recv()
#             if not data:
#                 break
#
#             message = data
#             print(message)
#             self.send_message(message)
#
#         print(f"[*] Connection closed with {websocket.remote_address}")
#
#     def run(self):
#         self.gossip_thread.start()
#         asyncio.run(self._server())

import asyncio
import json
import websockets
from websockets.exceptions import WebSocketException


class GossipNode:
    def __init__(self, host, port, peers: set):
        self.host = host
        self.port = port
        self.gossip_peers = peers
        self.chat_clients = set()
        self.message_log = []
        self.loop = asyncio.get_event_loop()

    async def run(self):
        start_server = websockets.serve(self._client_handler, self.host, self.port)
        await start_server
        print(f"Server listening on {self.host}:{self.port}")

        # Connect to peers
        for peer in self.gossip_peers:
            self.loop.create_task(self._connect_peer(peer))

        await self._run_forever()

    async def _run_forever(self):
        while True:
            await asyncio.sleep(1)

    async def _client_handler(self, websocket, path):
        self.chat_clients.add(websocket)
        try:
            async for message in websocket:
                print(f"[*] Received message from {websocket.remote_address}: {message}")
                self.send_message(message)
        except WebSocketException:
            self.chat_clients.remove(websocket)
        finally:
            self.chat_clients.remove(websocket)

    async def _connect_peer(self, peer):
        host, port = peer
        uri = f"ws://{host}:{port}"
        try:
            async with websockets.connect(uri) as websocket:
                self.gossip_peers.add(websocket)
                print(f"[*] Connected to peer {host}:{port}")
        except WebSocketException as e:
            print(f"[!] Failed to connect to peer {host}:{port} due to {str(e)}")

    def send_message(self, message):
        # Add the message to the local message log
        self.message_log.append(message)
        # Send the message to connected clients
        for client in self.clients:
            self.loop.create_task(client.send(f"Broadcast: {message}"))
        # Propagate the message to other gossip nodes
        self.loop.create_task(self._gossip(message))

    async def _gossip(self, message):
        for peer in self.gossip_peers:
            host, port = peer
            uri = f"ws://{host}:{port}"
            try:
                # TODO
                # если отправлять по http, то не будет проблем с тем что и клиенты и ноды ходят в одно место
                # или нужно как-то разруливать в функции handle_message откуда пришло
                # и нужно сделать согласование типо отправлять сообщения, только если тебе его согласовали обе соседние ноды
                # дальше можно попробовать складывать сообщения в какую-нибудь базу(массивчик) и еще ее пытаться согласовывать и всё

                async with websockets.connect(uri) as websocket:
                    await websocket.send(message)
            except WebSocketException as e:
                print(f"[!] Failed to gossip message to peer {host}:{port} due to {str(e)}")
