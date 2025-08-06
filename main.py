from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

DEPSEARCH_TOKEN = "3f740dd32d8cd9744615e3c4b871bd63"
user_tokens = set()

@app.post("/tokens")
async def create_token(token: str = Query(...)):
    if not token:
        raise HTTPException(status_code=400, detail="Token required")
    if token in user_tokens:
        raise HTTPException(status_code=400, detail="Token already exists")
    user_tokens.add(token)
    return {"message": "Token created", "token": token}

@app.delete("/tokens")
async def delete_token(token: str = Query(...)):
    if token in user_tokens:
        user_tokens.remove(token)
        return {"message": "Token deleted"}
    raise HTTPException(status_code=404, detail="Token not found")

@app.get("/")
async def proxy_search(path: str = Query(..., description="Format: token/query")):
    if '/' not in path:
        raise HTTPException(status_code=400, detail="Invalid path format. Use token/query")
    token, query = path.split('/', 1)
    if token not in user_tokens:
        raise HTTPException(status_code=403, detail="Invalid token")
    depsearch_url = f"https://api.depsearch.digital/quest={query}?token={DEPSEARCH_TOKEN}&lang=ru"
    try:
        r = requests.get(depsearch_url)
        r.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch from DepSearch: {str(e)}")
    return JSONResponse(content=r.json())