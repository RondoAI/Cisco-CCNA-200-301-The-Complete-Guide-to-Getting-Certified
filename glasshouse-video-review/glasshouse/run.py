"""Entry point: `python run.py` seeds data and serves the API + dashboard
at http://127.0.0.1:8000  (set GLASSHOUSE_LIVE=1 to pull live GDELT)."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("glasshouse.api:app", host="127.0.0.1", port=8000, reload=False)
