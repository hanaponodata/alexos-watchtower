"""
main.py
Enterprise-grade Watchtower FastAPI app entrypoint.
Bootstraps all routers, modules, background workers, and initializes the system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Import settings after .env loading
from config import settings, logger
from config.settings import reload_settings

# Reload settings to pick up environment variables
reload_settings()

# Import routers for all APIs here (you'll add these as you develop each API module)
from api.agents import router as agents_router
from api.events import router as events_router
from api.status import router as status_router
from api.auth import router as auth_router
from api.audit import router as audit_router
from api.forensic import router as forensic_router
# etc.

# Import ALEX OS Watchtower integration
from alexos_integration.api.watchtower_routes import register_watchtower_routes, set_watchtower_agent
from alexos_integration.modules.watchtower import create_watchtower_agent

# Import ALEX OS ChainBot integration
from alexos_integration.api.chainbot_routes import router as chainbot_router, initialize_chainbot_routes
from alexos_integration.modules.chainbot_agent import create_chainbot_agent

# Import dashboard router
from dashboard.api import router as dashboard_router

from fastapi.responses import FileResponse, JSONResponse
import json
import asyncio
from datetime import datetime
from websocket.manager import websocket_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Watchtower starting up...")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Node ID: {settings.node_id}")
    
    # Initialize ALEX OS Watchtower agent
    try:
        logger.info("Initializing ALEX OS Watchtower agent...")
        
        # Create Watchtower configuration
        watchtower_config = {
            'watchtower': {
                'update_interval': 300,  # 5 minutes
                'cleanup': True,
                'auto_update': False,  # Manual updates for safety
                'monitoring_enabled': True,
                'monitoring_interval': 30,  # 30 seconds
                'webhook_enabled': True,
                'log_level': 'INFO'
            }
        }
        
        # Create Watchtower agent
        watchtower_agent = create_watchtower_agent(
            "watchtower-001",
            "Watchtower Monitor",
            event_bus=None,  # Will be connected to ALEX OS event bus
            ledger=None,     # Will be connected to ALEX OS ledger
            config=watchtower_config
        )
        
        # Start the agent
        await watchtower_agent.start()
        
        # Set the agent reference for API routes
        set_watchtower_agent(watchtower_agent)
        
        # Register Watchtower routes
        register_watchtower_routes(app)
        
        logger.info("ALEX OS Watchtower agent initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize ALEX OS Watchtower agent: {e}")
        # Continue startup even if Watchtower fails
    
    # Initialize ALEX OS ChainBot agent
    try:
        logger.info("Initializing ALEX OS ChainBot agent...")
        
        # Create ChainBot configuration
        chainbot_config = {
            'chainbot': {
                'api_url': os.getenv('CHAINBOT_API_URL', 'http://localhost:3000'),
                'api_key': os.getenv('CHAINBOT_API_KEY'),
                'health_check_interval': 30,
                'sync_interval': 60
            }
        }
        
        # Create ChainBot agent
        chainbot_agent = create_chainbot_agent(
            "chainbot-001",
            "ChainBot Orchestrator",
            event_bus=None,  # Will be connected to ALEX OS event bus
            ledger=None,     # Will be connected to ALEX OS ledger
            config=chainbot_config
        )
        
        # Start the agent
        await chainbot_agent.start()
        
        # Initialize ChainBot routes with agent instance
        initialize_chainbot_routes(chainbot_agent)
        
        logger.info("ALEX OS ChainBot agent initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize ALEX OS ChainBot agent: {e}")
        # Continue startup even if ChainBot fails
    
    # Initialize background tasks, scheduler, health checks, etc.
    # TODO: Add background task initialization here
    
    yield
    
    # Shutdown
    logger.info("Watchtower shutting down...")
    
    # Stop Watchtower agent
    try:
        if 'watchtower_agent' in locals():
            await watchtower_agent.stop()
            logger.info("ALEX OS Watchtower agent stopped")
    except Exception as e:
        logger.error(f"Error stopping Watchtower agent: {e}")
    
    # Stop ChainBot agent
    try:
        if 'chainbot_agent' in locals():
            await chainbot_agent.stop()
            logger.info("ALEX OS ChainBot agent stopped")
    except Exception as e:
        logger.error(f"Error stopping ChainBot agent: {e}")
    
    # Cleanup, flush logs, etc.

app = FastAPI(
    title="Watchtower",
    description="Enterprise-grade agentic, sovereign, extensible OS and protocol",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
if settings.env == "production":
    # Disable HTTPS redirect for now - causing 307 redirects
    # app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["10.42.69.208", "localhost", "127.0.0.1"]
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://10.42.69.208:3000", "https://10.42.69.208"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers here, e.g.:
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(audit_router, prefix="/api/audit", tags=["audit"])
app.include_router(forensic_router, prefix="/api/forensic", tags=["forensic"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])
app.include_router(events_router, prefix="/api/events", tags=["events"])
app.include_router(status_router, prefix="/api/status", tags=["status"])

# Register ChainBot router
app.include_router(chainbot_router)

# Register dashboard router
app.include_router(dashboard_router, tags=["dashboard"])

# Mount static files at /static
app.mount("/static", StaticFiles(directory="dashboard/frontend/build/static"), name="static")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced WebSocket endpoint with authentication and audit logging."""
    client_id = None
    
    try:
        # Get authentication token from query parameters
        auth_token = websocket.query_params.get("token")
        
        # Connect using the WebSocket manager
        client_id = await websocket_manager.connect(websocket, auth_token)
        
        if not client_id:
            logger.warning("WebSocket connection failed - invalid authentication")
            return
        
        logger.info(f"WebSocket connected: {client_id}")
        
        # Main message handling loop
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=300.0)
                
                # Parse JSON message
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    # Send error for invalid JSON
                    await websocket_manager.send_message(client_id, {
                        "type": "error",
                        "message": "Invalid JSON format"
                    })
                    continue
                
                # Handle message using the manager
                response = await websocket_manager.handle_message(client_id, message)
                
                # Send response back to client
                if response:
                    await websocket_manager.send_message(client_id, response)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket_manager.send_message(client_id, {
                    "type": "ping",
                    "timestamp": datetime.utcnow().isoformat()
                })
                continue
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected normally: {client_id}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
    finally:
        # Cleanup connection
        if client_id:
            websocket_manager.disconnect(client_id, "connection_closed")

@app.get("/api/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics."""
    return websocket_manager.get_connection_stats()

@app.get("/api/health")
async def health_check():
    """Enhanced health check endpoint."""
    try:
        # Basic system health
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # WebSocket health
        ws_stats = websocket_manager.get_connection_stats()
        
        # Database health check
        from database.engine import get_session
        from sqlalchemy import text
        
        db_healthy = False
        try:
            db = next(get_session())
            db.execute(text("SELECT 1"))
            db.close()
            db_healthy = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
        
        health_status = {
            "status": "healthy" if db_healthy and cpu_percent < 90 and memory.percent < 90 else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "healthy" if db_healthy else "unhealthy",
                "cpu": "healthy" if cpu_percent < 90 else "warning",
                "memory": "healthy" if memory.percent < 90 else "warning",
                "disk": "healthy" if disk.percent < 90 else "warning",
                "websocket": "healthy" if ws_stats["active_connections"] >= 0 else "error"
            },
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "websocket_connections": ws_stats["active_connections"]
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }

# Serve index.html for all non-API, non-static routes (MUST BE LAST)
@app.get("/{full_path:path}", response_class=FileResponse)
def serve_react_app(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("static/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    index_path = os.path.join("dashboard", "frontend", "build", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"detail": "Not Found"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
