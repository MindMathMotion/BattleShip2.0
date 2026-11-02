# Two-player online starter

## Deploy backend (Render)
1. Push `server.py`, `requirements.txt`, and `render.yaml` to a GitHub repository.
2. In Render, create a new Blueprint from that repository, or create a Web Service with build command `pip install -r requirements.txt` and start command `uvicorn server:app --host 0.0.0.0 --port $PORT`.
3. Wait for deployment. Visit `https://YOUR-SERVICE.onrender.com/health` and check for `{"status":"ok"}`.

## Deploy frontend (GitHub Pages)
1. Replace `wss://REPLACE-WITH-YOUR-RENDER-SERVICE.onrender.com` in `index.html` with the `wss://` form of your Render service URL.
2. Put `index.html` in a GitHub Pages repository and enable Pages in repository Settings > Pages.
3. Open the published URL on two devices and join the same room code (e.g. ABCD).

## Notes
- This is a demonstration, not a secure production game. Room codes are not passwords.
- State is kept in memory; server restarts reset rooms. Run one server worker/instance.
- Render free services may sleep when idle; initial connections may take time.
- For production, add authentication, rate limiting, validated input, server-authoritative simulation and persistent/shared state.
