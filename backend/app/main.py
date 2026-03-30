from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import download, health, preview, result, solve, upload, validation

app = FastAPI(title="SCM MILP PoC API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router, prefix="/api")
app.include_router(validation.router, prefix="/api")
app.include_router(download.router, prefix="/api")
app.include_router(preview.router, prefix="/api")
app.include_router(solve.router, prefix="/api")
app.include_router(result.router, prefix="/api")


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "SCM MILP PoC backend is running."}
