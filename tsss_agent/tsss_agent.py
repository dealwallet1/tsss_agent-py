import os
import json
from typing import List, Dict, Literal
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from copilotkit import CopilotKitState
import meilisearch
from dotenv import load_dotenv
load_dotenv()
meilisearch_url = os.getenv("MEILISEARCH_SEARCH")
meilisearch_key = os.getenv("MEILISEARCH_SEARCH_KEY")
index_name = os.getenv("MEILISEARCH_INDEX_NAME")

class AgentState(CopilotKitState):
    language: Literal["english", "spanish"] = "english"
    context: List[Dict[str, str]] = []
    # details: Dict[str, str]
    user_input_query: str

async def search(query, index_name):
    print("=================>index_name", index_name)
    try:
        client = meilisearch.Client(meilisearch_url,meilisearch_key)
        search_results = client.index(index_name).search(
            query,
            {
                "limit": 10,
                "hybrid": {"semanticRatio": 0.7, "embedder": "default"},
                "showRankingScore": True,
                "rankingScoreThreshold": 0.8
            }
        )
        print("search_results===>", search_results)
        return search_results
        
    except Exception as e:
        print(f"Error in search: {e}")
        return []

async def chat_node(state: AgentState, config: RunnableConfig) -> Command[Literal["__end__"]]:
    try:
        # details = state.get("details", {})
        # print("details in chat node====>", details)
        
        user_input_query = state["messages"][-1].content
        print("user_input_query====>", user_input_query)

        context = await search(user_input_query, index_name)
     
        model = ChatOllama(model="qwen2.5vl:7b",base_url="https://ollama.dealwallet.com/",temperature=0.7)
        
      
        system_prompt = (
            f"You are a helpful assistant. Use the following context to answer the query in {state.get('language', 'english')}:\n"
            f"Context: {json.dumps(context)}\n"
            f"Query: {user_input_query}\n"
            f"if there is no relevant infpormation in the context the reply as feel free to ask regarding TSSS Infotech Company\n"
            f"If the input query is like greetings like hi, hello etc then reply with greetings reply on your own\n"

        )
        print("system_prompt==>", system_prompt)
        
        # Invoke model with system prompt and user query
        try:
            response = await model.ainvoke([system_prompt, user_input_query], config)
            print("response==>", response)
        except Exception as e:
            print(f"Error Model invocation failed: {e}")
            raise
        
        return Command(goto=END, update={"messages": response, "context": context})
    
    except Exception as e:
        print(f"Error in chat_node: {e}")
        return Command(goto=END, update={"messages": [], "context": []})

# Define workflow
workflow = StateGraph(AgentState)
workflow.add_node("chat_node", chat_node)
workflow.set_entry_point("chat_node")
graph = workflow.compile(MemorySaver())