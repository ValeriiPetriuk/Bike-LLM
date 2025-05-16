from fastapi import APIRouter, Depends

from auth.dependency import get_current_auth_user
from utils.async_utils import async_retry
from agents.bike_rag_agent import bike_rag_agent_executor
from models.bike_rag_query import BikeQueryOutput, BikeQueryInput, UserModel

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    return await bike_rag_agent_executor.ainvoke({"input": query})

@router.get("/")
async def get_status():
    return {"status": "running"}

@router.post("/bike-rag-agent")
async def query_bike_rag_agent(
        query: BikeQueryInput,
        user: UserModel = Depends(get_current_auth_user)
) -> BikeQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]
    return query_response
