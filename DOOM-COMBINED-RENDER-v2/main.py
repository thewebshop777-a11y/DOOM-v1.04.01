"""
DOOM AI — Core application
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

from config import settings
from db import init_schema

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_schema()
    except Exception as e:
        print(f"Schema init note: {e}")
    yield

app = FastAPI(
    title="DOOM AI",
    description="DOOM AI — Command operating system powered by PBE",
    version="10.3.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
from ratelimit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware, calls=120, window=60)

frontend_path = os.path.dirname(__file__)
if os.path.isdir(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "DOOM AI running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "10.3.0", "powers": 5}

# Absolute imports (works when run as script)
import doom_auth as auth
import inquiry
import powers
import connectors
import modules
import automations
import workspace
import spaces
import employees
import approvals
import settings as settings_router
import media
import power_tools
import autopilot_perms
import accounts
import permissions
import high_mgmt
import mid_mgmt
import finance
import psychology
import founder_tools
import comms
import memory
import pbe_manager
import pbe_bridge
import voice
import actions
import core
import hr
import founder
import designer
import login as login_router

app.include_router(power_tools.router, prefix="/api/power-tools", tags=["power-tools"])
app.include_router(autopilot_perms.router, prefix="/api/autopilot/permissions", tags=["autopilot-perms"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["permissions"])
app.include_router(high_mgmt.router, prefix="/api/high", tags=["high-management"])
app.include_router(mid_mgmt.router, prefix="/api/mid", tags=["middle-management"])
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
app.include_router(psychology.router, prefix="/api/psychology", tags=["psychology"])
app.include_router(founder_tools.router, prefix="/api/founder/tools", tags=["founder-tools"])
app.include_router(comms.router, prefix="/api/comms", tags=["comms"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(pbe_manager.router, prefix="/api/pbe/process", tags=["pbe-process"])
app.include_router(pbe_bridge.router, prefix="/api/pbe", tags=["pbe"])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(actions.router, prefix="/api/actions", tags=["actions"])
app.include_router(core.router, prefix="/api/core", tags=["core"])
app.include_router(hr.router, prefix="/api/hr", tags=["hr"])
app.include_router(founder.router, prefix="/api/founder", tags=["founder"])
app.include_router(designer.router, prefix="/api/designer", tags=["designer"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(inquiry.router, prefix="/api/inquiry", tags=["inquiry"])
app.include_router(powers.router, prefix="/api/powers", tags=["powers"])
app.include_router(connectors.router, prefix="/api/connectors", tags=["connectors"])
app.include_router(modules.router, prefix="/api/modules", tags=["modules"])
app.include_router(automations.router, prefix="/api/automations", tags=["automations"])
app.include_router(workspace.router, prefix="/api/workspace", tags=["workspace"])
app.include_router(spaces.router, prefix="/api/spaces", tags=["spaces"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(approvals.router, prefix="/api/approvals", tags=["approvals"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(login_router.router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.app_port))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
    )
