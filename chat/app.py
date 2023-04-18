#!/usr/bin/env python3
from aiohttp import web
from models.message import Message, MessageType


class WSChat:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.conns = {}
        self.users = set()

    async def main_page(self, request):
        return web.FileResponse('chat/templates/index.html')

    async def chat(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        while True:
            data = ''
            try:
                data = await ws.receive()
            except Exception:
                break
            try:
                new_data = data.json()
            except:
                dead = ''
                if str(data.data) == '1001':
                    for conn in self.conns:
                        if self.conns[conn].closed:
                            dead = conn
                    self.conns.pop(dead)
                    for conn in self.conns:
                        msg = Message(mtype=MessageType.USER_LEAVE, id="dead", text="no", to_id="nobody", gossip_id="TODO")
                        await self.conns[conn].send_json(msg.dict())
                continue

            if new_data['mtype'] == 'INIT':
                self.conns[new_data['id']] = ws
                for con in self.conns:
                    if con != new_data['id']:
                        msg = Message(mtype=MessageType.USER_ENTER, id=new_data['id'], text="no", to_id="nobody", gossip_id="TODO")
                        await self.conns[con].send_json(msg.dict())

            elif new_data['mtype'] == 'TEXT':
                if new_data['to'] is not None:
                    msg = Message(mtype=MessageType.DM, id=new_data['id'], text=new_data['text'], to_id=new_data['to'], gossip_id="TODO")
                    if new_data['to'] in self.conns:
                        await self.conns[new_data['to']].send_json(msg.dict())
                    continue
                for con in self.conns:
                    if con != new_data['id']:
                        msg = Message(mtype=MessageType.MSG, id=new_data['id'], text=new_data['text'], to_id="all", gossip_id="TODO")
                        await self.conns[con].send_json(msg.dict())

    def run(self):
        app = web.Application()
        app.router.add_get('/', self.main_page)
        app.router.add_get('/chat', self.chat)
        web.run_app(app, host=self.host, port=self.port)


if __name__ == '__main__':
    WSChat().run()
