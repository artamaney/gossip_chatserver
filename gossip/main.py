import asyncio

from gossip.authenticator import Authenticator, AuthenticatorSettings
from node import GossipNode
import threading


async def run_node(host, port, peers):
    node = GossipNode(host, port, peers, authenticator=Authenticator(AuthenticatorSettings()))
    await node.run()


if __name__ == "__main__":

    nodes = [
        ("localhost", 5000, {"localhost 5000": [("localhost", 5001), ("localhost", 5002)]}),
        ("localhost", 5001, {"localhost 5001": [("localhost", 5000), ("localhost", 5002)]}),
        ("localhost", 5002, {"localhost 5002": [("localhost", 5000), ("localhost", 5001)]}),
        ("localhost", 5003, {"localhost 5003": [("localhost", 5002)]})
    ]

    tasks = [run_node(host, port, peers) for host, port, peers in nodes]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()

