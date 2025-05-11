import os
# from langchain_community.graphs import Neo4jGraph
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
# from langchain.chains import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate



BIKE_QA_MODEL = os.getenv('BIKE_QA_MODEL')
BIKE_CYPHER_MODEL=os.getenv('BIKE_CYPHER_MODEL')


graph = Neo4jGraph(
    # url="bolt://localhost:7687",
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

cypher_generation_template = """
    Task:
    Generate Cypher query for a Neo4j graph database representing a bicycle store.
    
    Instructions:
    Use only the provided node labels, properties, and relationships from the schema.
    Do not use any other labels, properties, or relationships that are not listed.
    Return only the Cypher query without explanations or comments.
    
    Schema:
    {schema}
    
    Note:
    Do not include any explanations or apologies in your responses.
    Do not respond to any questions that might ask anything other than
    for you to construct a Cypher statement. Do not include any text except
    the generated Cypher statement. Make sure the direction of the relationship is
    correct in your queries. Make sure you alias both entities and relationships
    properly. Do not run any queries that would add to or delete from
    the database. Make sure to alias all statements that follow as with
    statement (e.g. WITH v as visit, c.billing_amount as billing_amount)
    If you need to divide numbers, make sure to
    filter the denominator to be non zero.
    Use `duration.between(date(...), date()).years` to calculate age.
    
    # Find all customers who purchased a product in the 'Road' line
    MATCH (c:Customer)-[:MADE]->(:Transaction)-[:CONTAINS]->(p:Product)
    WHERE p.product_line = 'Road'
    RETURN DISTINCT c.first_name + " " + c.last_name AS customer_name
     
    # What is the total revenue from online orders?
    MATCH (:Customer)-[:MADE]->(t:Transaction) - [:CONTAINS] -> (p:Product)
    WHERE t.online_order = True
    RETURN round(sum(p.price)) AS total_online_revenue
    
    # Which product line has the highest average list price?
    MATCH (:Transaction)-[:CONTAINS]->(p:Product)
    WITH p.product_line AS line, avg(p.price) AS avg_price
    RETURN line, round(avg_price)
    ORDER BY avg_price DESC
    LIMIT 1
    
    # Who is the customer with the most transactions?
    MATCH (c:Customer)-[:MADE]->(t:Transaction)
    WITH c, count(t) AS tx_count
    RETURN c.first_name + " " + c.last_name AS full_name, tx_count
    ORDER BY tx_count DESC
    LIMIT 1
    
    # How many customers from NSW have bought a product of brand 'Norco Bicycles'?  
     MATCH (c:Customer)-[:MADE]->(:Transaction)-[:CONTAINS]->(p:Product)
    WHERE c.state = 'NSW' AND p.brand = 'Norco Bicycles'
    RETURN count(DISTINCT c.customer_id) AS customers_from_NSW
    
    # Which year had the highest number of transactions?
    MATCH (:Customer)-[:MADE]->(t:Transaction)
    WITH date(t.date).year AS year, count(*) AS tx_count
    RETURN year, tx_count
    ORDER BY tx_count DESC
    LIMIT 1
    
    The question is:
    {question}
    
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)

qa_generation_template = """You are an assistant that takes the results
from a Neo4j Cypher query over a bicycle store graph database and forms
a natural-language response. The query results section contains the output
from a Cypher query generated based on a user's question. The output is
authoritative — do not use any external assumptions or general knowledge.

Query Results:
{context}

Question:
{question}

Instructions:
- If the results are empty (i.e., []), reply with: "I don't know the answer."
- Otherwise, use the results directly to answer the question in a clear,
  natural way.
- Always assume monetary values (e.g. list_price, profit) are in AUD
  unless otherwise noted.
- If the result contains customer names, ensure they are formatted clearly,
  e.g. "Jane Doe", even if there are commas or punctuation.
- If the result involves quantities, include them in the response.
- If there is a ranking (e.g. top product, best customer), make that clear
  in your answer.
- If a date or time duration is present, treat it as accurate and include
  it as is.

"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)

bike_cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(
        model=BIKE_QA_MODEL,
        base_url=os.getenv("BASE_URL_OPENROUTER"),
        api_key=os.getenv("API_KEY_OPENROUTER"),
        temperature=0
    ),
    qa_llm=ChatOpenAI(
        model=BIKE_CYPHER_MODEL,
        base_url=os.getenv("BASE_URL_OPENROUTER"),
        api_key=os.getenv("API_KEY_OPENROUTER"),
        temperature=0
    ),
    graph=graph,
    verbose=True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    tok_k=100,
    allow_dangerous_requests=True,
)