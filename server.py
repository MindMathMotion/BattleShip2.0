import asyncio
import os
from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['GET'], allow_headers=['*'])
rooms = defaultdict(dict)
lock = asyncio.Lock()

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.websocket('/game/{room_id}')
async def game(ws: WebSocket, room_id: str):
    room_id = room_id.upper()
    if not (4 <= len(room_id) <= 12 and room_id.isalnum()):
        await ws.close(code=1008)
        return
    await ws.accept()
    async with lock:
        room = rooms[room_id]
        available = next((i for i in (1, 2) if i not in room), None)
        if available is not None:
            room[available] = ws
        players = list(room.items())
    if available is None:
        await ws.send_json({'type': 'error', 'message': 'Room is full'})
        await ws.close()
        return
    await ws.send_json({'type': 'joined', 'player': available, 'room': room_id})
    for _, peer in players:
        try:
            await peer.send_json({'type': 'players', 'count': len(players)})
        except Exception:
            pass
    try:
        while True:
            message = await ws.receive_json()
            if message.get('type') != 'move':
                continue
            x, y = message.get('x'), message.get('y')
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                continue
            event = {'type': 'move', 'player': available, 'x': max(0, min(100, x)), 'y': max(0, min(100, y))}
            for _, peer in list(rooms[room_id].items()):
                try:
                    await peer.send_json(event)
                except Exception:
                    pass
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        async with lock:
            room = rooms.get(room_id, {})
            if room.get(available) is ws:
                del room[available]
            peers = list(room.values())
            if not room:
                rooms.pop(room_id, None)
        for peer in peers:
            try:
                await peer.send_json({'type': 'players', 'count': len(peers)})
                await peer.send_json({'type': 'left', 'player': available})
            except Exception:
                pass
