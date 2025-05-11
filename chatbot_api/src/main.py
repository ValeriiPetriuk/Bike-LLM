from fastapi import FastAPI
from agents.bike_rag_agent import bike_rag_agent_executor
from models.bike_rag_query import BikeQueryOutput, BikeQueryInput
from utils.async_utils import async_retry

app = FastAPI(
    title="Bike Shop ChatBot",
    description="Bike Shop ChatBot",
)

@async_retry(max_retries=10, delay=1)
async def invoke_agent_with_retry(query: str):
    return await bike_rag_agent_executor.ainvoke({"input": query})

@app.get("/")
async def get_status():
    return {"status": "running"}


@app.post("/bike-rag-agent")
async def query_bike_rag_agent(query: BikeQueryInput) -> BikeQueryOutput:
    query_response = await invoke_agent_with_retry(query.text)
    query_response["intermediate_steps"] = [
        str(s) for s in query_response["intermediate_steps"]
    ]
    return query_response

