import os
# from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_neo4j import Neo4jVector
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
# from langchain.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

BIKE_QA_MODEL = os.getenv("BIKE_QA_MODEL")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=embeddings,
    # url="bolt://localhost:7687",
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="customers",
    node_label="Customer",
    text_node_properties=[
        "first_name",
        "last_name",
        "gender",
        "country",
        "job_title",
        "job_industry_category",
        "wealth_segment",
        "owns_car",
        "state",
        "past_3_years_bike_related_purchases"
    ],
    embedding_node_property="embedding",
)

customer_template = """
Your job is to answer questions about customers 
in a bicycle store database. Use only the context provided to answer 
the questions. 

If the answer cannot be found in the context, respond with "I don't know".

{context}
"""


customer_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=customer_template)
)

customer_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [customer_system_prompt, customer_human_prompt]


customer_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

customer_vector_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(
        model=BIKE_QA_MODEL,
        base_url=os.getenv("BASE_URL_OPENROUTER"),
        api_key=os.getenv("API_KEY_OPENROUTER"),
        temperature=0
    ),
    chain_type="stuff",
    retriever=neo4j_vector_index.as_retriever(k=10),
)

customer_vector_chain.combine_documents_chain.llm_chain.prompt = customer_prompt





