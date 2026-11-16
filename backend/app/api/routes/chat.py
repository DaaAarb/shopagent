from fastapi import APIRouter

from app.agent.agent import ChatReply
from app.api.deps import AgentDep, CurrentUserId
from app.dtos import ChatConfirm, ChatMessageCreate

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatReply)
def chat(body: ChatMessageCreate, user_id: CurrentUserId, agent: AgentDep):
    return agent.chat(user_id, body.message)


@router.post("/confirm", response_model=ChatReply)
def confirm(body: ChatConfirm, user_id: CurrentUserId, agent: AgentDep):
    return agent.confirm(user_id, body.action_id, body.approve)
