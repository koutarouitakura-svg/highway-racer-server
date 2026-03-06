import asyncio
import websockets
import json

rooms = {}

async def handler(ws):
    player_id = None
    room_id   = None
    try:
        msg = await ws.recv()
        init = json.loads(msg)
        room_id   = init["room"]
        player_id = init["player_id"]

        if room_id not in rooms:
            rooms[room_id] = {}
        rooms[room_id][player_id] = ws
        print(f"[JOIN] {player_id} -> room:{room_id}  ({len(rooms[room_id])} players)")

        async for raw in ws:
            room = rooms.get(room_id, {})
            targets = [w for pid, w in room.items() if pid != player_id]
            if targets:
                await asyncio.gather(*[t.send(raw) for t in targets],
                                     return_exceptions=True)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if room_id and player_id and room_id in rooms:
            rooms[room_id].pop(player_id, None)
            if not rooms[room_id]:
                del rooms[room_id]
            print(f"[LEAVE] {player_id} left room:{room_id}")

async def main():
    print("Server started on port 8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

asyncio.run(main())