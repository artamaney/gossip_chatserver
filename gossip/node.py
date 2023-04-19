import asyncio
import json
import websockets
from websockets.exceptions import WebSocketException

from gossip.authenticator import Authenticator
from gossip.utils import check_if_json


class GossipNode:
    def __init__(self, host, port, peers: set, authenticator: Authenticator):
        self.host = host
        self.port = port
        self.adjacency_list = peers
        self.gossip_peers = set()
        self.chat_clients = set()
        self.message_log = []
        self.loop = asyncio.get_event_loop()
        self.users = set()
        self.messages = set()
        self.authenticator = authenticator

    async def run(self):
        start_server = websockets.serve(self._handle_message, self.host, self.port)
        await start_server
        print(f"Server listening on {self.host}:{self.port}")

        self._gossip_dfs(f"{self.host} {self.port}", self.adjacency_list)

        await self._run_forever()

    def _gossip_dfs(self, peer, adjacency_list=None, is_connect=True, message=""):
        if adjacency_list is None:
            adjacency_list = self.adjacency_list

        print(f"{self.host} {self.port}", "peer", peer)
        for vertex in adjacency_list.get(peer, []):
            print(f"{self.host} {self.port}", ("peer", peer), ("vertex", vertex))
            if is_connect:
                self.loop.create_task(self._connect_peer(vertex, adjacency_list))
            else:
                print("AAAAAAAAAAAAAAAAA")
                self.loop.create_task(self._gossip(vertex, adjacency_list, message))

    async def _run_forever(self):
        while True:
            await asyncio.sleep(1)

    async def _handle_message(self, websocket, path):
        match path:
            case "/gossip_node/connect":
                async for message in websocket:
                    data = json.loads(message)
                    self._gossip_dfs(f"{self.host} {self.port}", data["adjacency_list"])
            case "/gossip_node/send_message":
                async for message in websocket:
                    data = json.loads(message)
                    print(f"[*] Received message from node {websocket.remote_address}: {data}")
                    self.send_message(data["message"], data["adjacency_list"])

            case "/chat":
                self.chat_clients.add(websocket)
                try:
                    async for message in websocket:
                        print(f"[*] Received message from {websocket.remote_address}: {message}")
                        self.send_message(message, self.adjacency_list)
                except WebSocketException:
                    self.chat_clients.remove(websocket)
                finally:
                    self.chat_clients.remove(websocket)

    async def _connect_peer(self, peer, adjacency_list=None):
        if adjacency_list is None:
            adjacency_list = self.adjacency_list

        host, port = peer
        uri = f"ws://{host}:{port}/gossip_node/connect"
        try:
            async with websockets.connect(uri) as websocket:
                self.gossip_peers.add(websocket)
                data = dict(adjacency_list=adjacency_list)
                print(data)
                message = json.dumps(data)
                await websocket.send(message)
                print(f"[*] Connected to peer {host}:{port}")
        except WebSocketException as e:
            print(f"[!] Failed to connect to peer {host}:{port} due to {str(e)}")

    def send_message(self, message, adjacency_list):
        self.messages.add(message)

        for client in self.chat_clients:
            self.loop.create_task(client.send(f"Broadcast: {message}"))

        self._gossip_dfs(f"{self.host} {self.port}", adjacency_list, False, message)

    async def _gossip(self, peer, adjacency_list, message):
        host, port = peer
        uri = f"ws://{host}:{port}/gossip_node/send_message"
        try:
            async with websockets.connect(uri) as websocket:
                data = dict(adjacency_list=adjacency_list, message=message)
                message = json.dumps(data)

                await websocket.send(message)
        except WebSocketException as e:
            print(f"[!] Failed to gossip message to peer {host}:{port} due to {str(e)}")
