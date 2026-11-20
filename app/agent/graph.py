import os
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from app.tools.erp_tools import check_inventory_stock, calculate_order_quote

# 1. Bind ERP tools to the model
tools = [check_inventory_stock, calculate_order_quote]
openai_api_key = os.getenv("OPENAI_API_KEY", "mock-key-for-dev")

model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=openai_api_key
).bind_tools(tools)

# 2. Node logic
def call_model(state: MessagesState):
    system_prompt = SystemMessage(
        content=(
            "You are an advanced Intelligent ERP Agent for industrial inventory and order management. "
            "You have access to tools to check inventory stock levels and calculate order quotes with volume discounts. "
            "Always use tools when a user asks about specific items, stock quantities, or pricing quotes."
        )
    )
    response = model.invoke([system_prompt] + state["messages"])
    return {"messages": [response]}

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 3. Assemble the State Graph
workflow = StateGraph(MessagesState)

workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END,
    },
)

workflow.add_edge("tools", "agent")

# 4. Compile with checkpoint for thread persistence
memory_checkpointer = MemorySaver()
app_graph = workflow.compile(checkpointer=memory_checkpointer)