# smoke_tool_call_roundtrip.py
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from open_deep_research.arxiv_tool import arxiv_search

# Build the model with tools bound (no temperature for gpt-5-mini)
llm = ChatOpenAI(model="gpt-5-mini")
tools = [arxiv_search]
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

# 1) Ask the model to use the tool
messages = [HumanMessage(content=(
    "Use the `arxiv_search` tool to fetch 2 recent arXiv papers on "
    "'state space models' and include links."
))]
ai_msg = llm_with_tools.invoke(messages)
print("TOOL CALLS:", ai_msg.tool_calls)

# 2) Execute each tool call and append ToolMessage(s)
for tc in ai_msg.tool_calls or []:
    result = tools_by_name[tc["name"]].invoke(tc["args"])
    messages.append(ai_msg)  # include the AI message that requested the tool
    messages.append(ToolMessage(content=result, tool_call_id=tc["id"]))

# 3) Ask the model to produce the final answer using the tool outputs
final = llm.invoke(messages)  # unbound is fine for a single-round demo
print("\nFINAL ANSWER:\n")
print(final.content)