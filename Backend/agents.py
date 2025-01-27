from langchain.agents import Tool, AgentType, initialize_agent
from langchain_community.chat_models import ChatOpenAI
from gpt_handler import chat_with_gpt
from vector_manager import live_store
from partselect_scrapper import scrape_partselect
import json

def scrape_partselect_tool(query: str) -> str:
    """
    Calls the scrape_partselect function, returns JSON with product details, Q&A, etc.
    """
    url = query.strip()
    if not url.startswith("https://"):
        return "Please provide a valid PartSelect URL."

    data = scrape_partselect(url)
    return json.dumps(data, indent=2)

def index_tool(query: str) -> str:
    """
    Index new PartSelect data from Google into ephemeral vector memory.
    """
    return live_store.live_search_and_index(query)

def search_tool(query: str) -> str:
    """
    Perform semantic search in ephemeral store to see if we already have relevant data.
    """
    results = live_store.semantic_search(query)
    if not results:
        return "No relevant data found in ephemeral store."
    return "\n\n".join(results)

def gpt_tool(query: str) -> str:
    """
    Direct GPT conversation. This can be used for final answer composition or fallback.
    """
    system_msg = {
        "role": "system",
        "content": (
            "You are a helpful chatbot specialized in PartSelect queries for "
            "refrigerator and dishwasher parts. Use the provided data or your training knowledge, "
            "but remain within that domain. If not relevant to parts, politely decline."
        )
    }
    user_msg = {
        "role": "user",
        "content": query
    }
    return chat_with_gpt([system_msg, user_msg])

# Define Tools
tool_index = Tool(
    name="index_google_data",
    func=index_tool,
    description="Fetch fresh data from Google about PartSelect. Provide the query, and it will index new snippet data."
)
tool_search = Tool(
    name="semantic_search",
    func=search_tool,
    description="Search previously indexed PartSelect data for relevant snippets."
)
tool_gpt = Tool(
    name="gpt_tool",
    func=gpt_tool,
    description="Use GPT for conversation or final answer composition."
)

tool_scrape_partselect = Tool(
    name="scrape_partselect_data",
    func=scrape_partselect_tool,
    description=(
        "Scrape a PartSelect product page (URL) to get structured data: "
        "product info, troubleshooting, Q&A, etc. Input must be a full https:// partselect.com link."
    )
)

def plan_and_execute_agent(query: str) -> str:
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    prefix_prompt = (
        "You are a PartSelect chat agent. You have the following tools:\n"
        "1) index_google_data: for snippet data from Google.\n"
        "2) semantic_search: to retrieve data you have indexed.\n"
        "3) scrape_partselect_data: to directly scrape a PartSelect product page for details.\n"
        "4) gpt_tool: to synthesize a final answer.\n"
        "Only talk about refrigerator and dishwasher parts, or relevant queries from partselect.com.\n"
        "Now, let's figure out how best to answer the user's query."
    )

    agent = initialize_agent(
        tools=[
            tool_index,
            tool_search,
            tool_scrape_partselect, 
            tool_gpt,
        ],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs={"prefix": prefix_prompt}
    )

    try:
        response = agent.run(query)
    except Exception as e:
        response = f"Agent error: {str(e)}"
    return response

