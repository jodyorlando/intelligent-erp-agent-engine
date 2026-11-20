from fastapi import APIRouter, Depends, HTTPException, status
from celery.result import AsyncResult
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.core.celery_app import celery_app, generate_pdf_quote_task

router = APIRouter(prefix="/api/v1/tasks", tags=["Async Tasks"])

class QuoteTaskRequest(BaseModel):
    item_code: str
    quantity: int
    customer_tier: str = "Standard"

@router.post("/export-quote")
async def trigger_quote_export(
    payload: QuoteTaskRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Dispatch a heavy background PDF quote generation task to Celery.
    """
    task = generate_pdf_quote_task.delay(
        item_code=payload.item_code,
        quantity=payload.quantity,
        customer_tier=payload.customer_tier
    )
    return {
        "message": "Quote generation task dispatched successfully.",
        "task_id": task.id,
        "status": "processing"
    }

@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Poll the status and result of a background Celery task by ID.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == "PENDING":
        return {"task_id": task_id, "state": task_result.state, "status": "Task pending or in queue..."}
    elif task_result.state == "SUCCESS":
        return {"task_id": task_id, "state": task_result.state, "result": task_result.result}
    elif task_result.state == "FAILURE":
        return {"task_id": task_id, "state": task_result.state, "error": str(task_result.info)}
    
    return {"task_id": task_id, "state": task_result.state}