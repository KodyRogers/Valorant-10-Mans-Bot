from fastapi import WebSocket

class DraftConnectionManager:

    def __init__(self):
        self.connections = {}

    async def connect(self, match_code: str, websocket: WebSocket):
        await websocket.accept()

        self.connections.setdefault(match_code, [])
        self.connections[match_code].append(websocket)

    def disconnect(self, match_code: str, websocket: WebSocket):
        if match_code in self.connections:
            self.connections[match_code].remove(websocket)

            if not self.connections[match_code]:
                del self.connections[match_code]

    async def broadcast(self, match_code: str, data: dict):
        if match_code not in self.connections:
            return

        for websocket in self.connections[match_code]:
            await websocket.send_json(data)

draft_connections = DraftConnectionManager()