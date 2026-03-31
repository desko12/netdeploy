from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.db_session import init_db
from app.routers import routers, vlans, interfaces, routing, config_logs, web, lab_deploy

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="NETCONF Router Manager - Interface web pour configurer les routeurs Cisco IOS-XE via NETCONF/YANG",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.router)
app.include_router(vlans.router)
app.include_router(interfaces.router)
app.include_router(routing.router)
app.include_router(config_logs.router)
app.include_router(web.web)
app.include_router(lab_deploy.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
