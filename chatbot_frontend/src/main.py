import os
import requests
import streamlit as st

CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8000/bike-rag-agent")

with st.sidebar:
    st.header("About the Bike Store Assistant")
    st.markdown(
        """
        This chatbot interfaces with a system that can answer questions about
        customers, orders, products, transactions, demographics, and addresses
        from a synthetic bike store database.
        """
    )
    st.header("Example Questions")
    st.markdown("- Which bikes are the top sellers?")
    st.markdown("- Who is the top customer by total spending?")
    st.markdown("- What is the average transaction amount?")
    st.markdown("- How many orders came from Victoria?")
    st.markdown("- What are the most popular bike brands?")
    st.markdown("- Which product categories have the lowest sales?")
    st.markdown("- Which customers live in Melbourne?")
    st.markdown("- How many purchases has customer ID 123 made?")
    st.markdown("- What is the average age of customers who bought a helmet?")
    st.markdown("- What is the total sales revenue for 2023?")

st.title("Bike Store Chatbot")

st.info(
    "Ask me anything about customers, orders, products, transactions, addresses, and more!"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message:
            st.markdown(message["output"])

        if "explanation" in message:
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])


if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)

    st.session_state.messages.append({"role": "user", "output": prompt})

    data = {"text": prompt}

    with st.spinner("Searching for an answer..."):
        response = requests.post(CHATBOT_URL, json=data)

        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]
        else:
            output_text = "An error occurred while processing your request. Please try again."
            explanation = ""

    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated", state="complete").info(explanation)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "output": output_text,
            "explanation": explanation,
        }
    )