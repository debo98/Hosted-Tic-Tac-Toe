import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)  # → src/
STATIC_DIR = os.path.join(BASE_DIR, "public")  # → src/public


# --- Game Manager (in-memory for prototype) ---
class Game:
    def __init__(self):
        self.connections: set[WebSocket] = set()
        self.lock = asyncio.Lock()
        self.board = [None] * 9
        self.turn = "X"
        self.players: dict[WebSocket, str] = {}  # maps first two sockets → "X"/"O"
        self.game_over = False

    async def broadcast(self, msg: dict):
        living = set()
        for ws in list(self.connections):
            try:
                await ws.send_json(msg)
                living.add(ws)
            except WebSocketDisconnect:
                # client went away — just drop it
                continue
            except Exception as e:
                # unexpected error — log it
                logger.error(f"Error sending ws message: {e}")
        self.connections = living

    async def join(self, ws: WebSocket):
        async with self.lock:
            await ws.accept()

            # Assign X or O, up to two
            if len(self.players) < 2:
                role = "X" if "X" not in self.players.values() else "O"
                self.players[ws] = role
                await ws.send_json({"type": "role", "role": role})
            else:
                # treat as spectator
                await ws.send_json({"type": "role", "role": "Spectator"})

            self.connections.add(ws)
            # send current board+turn
            await ws.send_json({"type": "state", "board": self.board, "turn": self.turn})

    async def move(self, idx: int, ws: WebSocket):
        async with self.lock:
            if self.players.get(ws) != self.turn or self.game_over:
                return
            if self.board[idx] is None:
                self.board[idx] = self.turn
                self.turn = "O" if self.turn == "X" else "X"
                await self.broadcast({"type": "state", "board": self.board, "turn": self.turn})
                winner = self.check_win()
                if winner or all(self.board):
                    self.game_over = True  # ← set flag
                    await self.broadcast({"type": "gameover", "winner": winner or "Draw"})

    async def restart(self):
        async with self.lock:
            # only actually clear state if previous game finished
            if not self.game_over:
                return
            self.board = [None] * 9
            self.turn = "X"
            self.game_over = False  # ← reset flag
            await self.broadcast({"type": "state", "board": self.board, "turn": self.turn})
            await self.broadcast({"type": "gameover", "winner": None})

    def check_win(self):
        wins = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
        for a, b, c in wins:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None


games: dict[str, Game] = {}


# --- WebSocket endpoint ---
@app.websocket("/ws/{game_id}")
async def websocket_endpoint(ws: WebSocket, game_id: str):
    game = games.setdefault(game_id, Game())
    await game.join(ws)

    try:
        while True:
            data = await ws.receive_json()
            action = data.get("action")

            if action == "move":
                await game.move(int(data["idx"]), ws)

            elif action == "restart":
                # only restart if the last game finished
                await game.restart()

    except WebSocketDisconnect:
        game.connections.discard(ws)
        game.players.pop(ws, None)
        if not game.connections:
            games.pop(game_id, None)


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
