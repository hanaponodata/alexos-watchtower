"""
api/agents.py
Agent registration and listing API endpoints for Watchtower.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from database.engine import get_session
from database.models.agents import Agent

router = APIRouter(prefix="/api/agents", tags=["agents"])

class AgentCreate(BaseModel):
    uuid: str = Field(..., description="Unique agent UUID")
    name: str
    agent_type: str
    owner: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "offline"
    score: Optional[int] = 0
    agent_metadata: Optional[dict] = Field(default_factory=dict)
    crypto_id: Optional[str] = None

class AgentOut(BaseModel):
    id: int
    uuid: str
    name: str
    agent_type: str
    owner: Optional[str]
    description: Optional[str]
    status: str
    score: int
    last_seen: Optional[str]
    agent_metadata: dict
    crypto_id: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=AgentOut)
def register_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = Agent(
        uuid=agent.uuid,
        name=agent.name,
        agent_type=agent.agent_type,
        owner=agent.owner,
        description=agent.description,
        status=agent.status,
        score=agent.score,
        agent_metadata=agent.agent_metadata,
        crypto_id=agent.crypto_id,
    )
    db.add(db_agent)
    try:
        db.commit()
        db.refresh(db_agent)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Agent registration failed: {e}")
    return db_agent

@router.get("/", response_model=List[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return agents
