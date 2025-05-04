# Tic-Tac-Toe PvP Prototype (FastAPI + WebSocket)

A minimal, real-time Tic-Tac-Toe game built with **FastAPI** and native **WebSocket** support, paired with a zero-bundler HTML/JS front-end. Designed as a lightweight prototype that can scale by swapping the in-memory game store for Redis pub/sub and running multiple Uvicorn workers.

## Features

- **Real-time gameplay** via WebSockets  
- **Room-based**: support multiple independent games by `game_id`  
- **Role assignment**: first two connections become **X** and **O**, extras spectate  
- **In-memory game store** (drop-in Redis pub/sub replacement for production)  
- **Restart guard**: “Restart” button only appears after a win or draw  
- **Zero build step**: plain HTML/CSS/JS, no bundler required  

## Prerequisites

- Python **3.9+**  
- (Optional) `git` CLI for cloning  

## Installation

```bash
# 1. Clone the repository
git clone git@github.com:you/your-repo.git
cd tic-tac-toe-fastapi

# 2. Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# On Windows:
# .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Start the FastAPI server with live reload on static files:
uvicorn src.server:app \
  --reload \
  --reload-dir src/public \
  --host 0.0.0.0 \
  --port 3000
```

1. Open **two** browser tabs (or share the URL) at `http://localhost:3000`.  
2. When prompted, enter the **same** game room ID in both.  
3. The first tab becomes **X**, the second **O**, any additional tabs spectate.  
4. Click cells to play. Once the game ends, the **Restart** button appears.  

## Example Console Output

```bash
INFO:     Started server process [12345]
INFO:     Uvicorn running on http://0.0.0.0:3000 (Press CTRL+C to quit)

# In browser console:
Attempting WS connection to ws://localhost:3000/ws/room42
WebSocket open
← message {type: "state", board: [null,...], turn: "X"}
← message {type: "state", board: ["X",null,...], turn: "O"}
← message {type: "gameover", winner: "X"}
```

## Deployment

- **Port**: default `3000`; override via the `$PORT` environment variable when deploying  
- **Static files**: served from `src/public` by FastAPI’s `StaticFiles`  
- **Scaling**:  
  1. Swap the in-memory `Game` class for a Redis-based pub/sub backend  
  2. Run multiple Uvicorn workers (`--workers N`) behind a load balancer  

## .gitignore

```gitignore
venv/
__pycache__/
*.py[cod]
.DS_Store
```
