from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Represents the execution state of the ERP agentic workflow graph.
    `messages` automatically appends new LLM outputs and tool responses.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_tier: str