from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

CODA_API_KEY  = os.environ["CODA_API_KEY"]
CODA_DOC_ID   = os.environ["CODA_DOC_ID"]
CODA_TABLE_ID = os.environ["CODA_TABLE_ID"]


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/check")
async def check_user(email: str = Query(...)):
    url = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}/tables/{CODA_TABLE_ID}/rows"
    headers = {"Authorization": f"Bearer {CODA_API_KEY}"}
    params  = {"query": f"Gmail:{email}"}

    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, params=params, timeout=10)

    if r.status_code != 200:
        return {"status": "error", "code": r.status_code, "detail": r.text}

    items = r.json().get("items", [])
    if not items:
        return {
            "status": "not_found",
            "message": "此 Gmail 尚未申請，請先填寫申請表"
        }

    values = items[0].get("values", {})
    status = values.get("狀態", "待審")
    name   = values.get("姓名", "")
    role   = values.get("職業", "")
    note   = values.get("審核備註", "")

    if status == "核准":
        return {"status": "approved", "name": name, "role": role}
    elif status == "待審":
        return {"status": "pending", "message": "申請審核中，請耐心等候通知"}
    else:
        msg = f"申請未通過。{note}" if note else "申請未通過，請聯繫管理員"
        return {"status": "rejected", "message": msg}
