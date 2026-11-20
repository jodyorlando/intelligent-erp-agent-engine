import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import HumanMessage
from app.database import get_db
from app.agent.graph import app_graph
from app.schemas import AgentPromptRequest, AgentRunResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/agent", tags=["ERP Agent Engine"])


@router.post("/run", response_model=AgentRunResponse)
async def run_erp_agent(payload: AgentPromptRequest, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Execute a multi-step ERP reasoning prompt through the LangGraph agentic workflow.
    """
    try:
        thread_id = payload.thread_id or f"thread_{uuid.uuid4().hex[:8]}"
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "messages": [HumanMessage(content=payload.prompt)]
        }
        
        # Invoke state graph asynchronously
        result = await app_graph.ainvoke(initial_state, config=config)
        messages = result.get("messages", [])
        final_message = messages[-1].content if messages else "No response generated."

        # Extract raw tool calls from message history for auditing
        executed_tool_calls = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                executed_tool_calls.extend(msg.tool_calls)

        return {
            "run_id": f"run_{uuid.uuid4().hex[:8]}",
            "prompt": payload.prompt,
            "final_response": final_message,
            "tool_calls": executed_tool_calls,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stream")
async def stream_erp_agent(payload: AgentPromptRequest, current_user: dict = Depends(get_current_user)):
    """
    Stream agent execution steps and tool calls in real-time via Server-Sent Events (SSE).
    """
    thread_id = payload.thread_id or f"thread_{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {"messages": [HumanMessage(content=payload.prompt)]}

    async def event_generator():
        #Stream updates from graph execution
        async for event in app_graph.astream_events(initial_state, config=config, version="v2"):
            kind = event.get("event")

            #Stream model output tokens or tool start/end
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"

            elif kind == "on_tool_start":
                tool_name = event.get("name")
                tool_inputs = event.get("data", {}).get("input")
                yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name, 'input': tool_inputs})}\n\n"
            
            elif kind == "on_tool_end":
                tool_name = event.get("name")
                tool_output = event.get("data", {}).get("output")
                yield f"data: {json.dumps({'type': 'tool_end', 'tool': tool_name, 'output': str(tool_output)})}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")