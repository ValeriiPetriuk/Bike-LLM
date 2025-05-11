import os
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_react_agent,
    Tool,
    AgentExecutor
)
from langchain import hub
from chains.customer_chain import customer_vector_chain
from chains.bike_cypher_chain import bike_cypher_chain
from tools.bike_tools import BikeTool

BIKE_AGENT_MODEL = os.getenv("BIKE_AGENT_MODEL")

bike_agent_prompt = hub.pull("hwchase17/react")

bike_tools = BikeTool()

tools = [
    Tool(
        name="Customer",
        func=customer_vector_chain.invoke,
        description="""
            Useful for answering subjective questions about customers, 
            such as preferences, demographics, or past purchases. 
            Examples: 
            - "What industry does Roddy work in?"
            - "Which customers live in Australia?"
            Avoid for quantitative queries (counts, totals, etc.).
            Input the entire question verbatim.
        """
    ),
    Tool(
        name="Graph",
        func=bike_cypher_chain.invoke,
        description="""
            Answers factual questions about products, transactions, 
            revenue, and customer activity using database queries.
            Examples:
            - "Total sales of road bikes in 2017?"
            - "Top 5 customers by purchase volume."
            - "How many customers from NSW have bought a product of brand 'Norco Bicycles'? "
            Input the entire question verbatim.
        """
    ),
    Tool(
        name="Cost",
        func=bike_tools.get_service_cost,
        description="""
            Provides estimated maintenance costs for specific bike brands.
            Examples:
            - "What’s the service cost for Trek bikes?"
            - "How much to service a Giant bicycle?"
            Input only the brand name (e.g., "Trek").
        """
    ),
    Tool(
        name="Availability",
        func=bike_tools.get_most_available_service,
        description="""
            Identifies brands with the lowest service costs.
            Example output: 
            - "Brand X offers the cheapest service at $30."
            No input required.
        """
    )
]

chat_model = ChatOpenAI(
    model=BIKE_AGENT_MODEL,
    base_url=os.getenv("BASE_URL_OPENROUTER"),
    api_key=os.getenv("API_KEY_OPENROUTER"),
    temperature=0
)

bike_rag_agent = create_react_agent(
    llm=chat_model,
    prompt=bike_agent_prompt,
    tools=tools,
)

bike_rag_agent_executor = AgentExecutor(
    agent=bike_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True
)