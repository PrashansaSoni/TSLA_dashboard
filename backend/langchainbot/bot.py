from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
import os
import pandas as pd
from langchainbot.agentTools import (
    tools,
    count_bullish_days,
    search_context,
    max_closing_price,
    min_opening_price,
    average_closing_price,
    total_volume,
    percentage_change,
    top_volume_days,
)
from langchain_groq import ChatGroq

# Environment variables
from dotenv import load_dotenv
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=groq_api_key
    )

def ask_groq(query: str):
    llm_with_tools = llm.bind_tools(tools)
    query = query
    prompt = ChatPromptTemplate([
    ("system","you are a expert financial agent and you have tools to call if required don't have to give your own answer"),
    ("user","here is your query {query}")])
    prompt = prompt.invoke({"query": query})
    messages = [HumanMessage(query)]
    ai_msg = llm_with_tools.invoke(prompt)

    for tool_call in ai_msg.tool_calls:
        selected_tool = {
            "count_bullish_days": count_bullish_days,
            "search_context": search_context,
            "max_closing_price": max_closing_price,
            "min_opening_price": min_opening_price,
            "average_closing_price": average_closing_price,
            "total_volume": total_volume,
            "percentage_change": percentage_change,
            "top_volume_days": top_volume_days
        }[tool_call["name"].lower()]
        tool_msg = selected_tool.invoke(tool_call)
        messages.append(tool_msg)


    result = llm.invoke(messages).content
    print(result)
    return result
