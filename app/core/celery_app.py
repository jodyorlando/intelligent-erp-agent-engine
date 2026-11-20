import time
from celery import Celery
from app.config import settings

celery_app = Celery(
    "erp_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="tasks.generate_pdf_quote")
def generate_pdf_quote_task(item_code: str, quantity: int, customer_tier: str) -> dict:
    """
    Simulates a heavy background job, such as building a formal PDF quote
    document and uploading it to cloud storage.
    """
    time.sleep(5)  # Simulate 5-second heavy background PDF generation
    
    unit_price = 4.50 if item_code.upper() == "6204-2RS" else 15.00
    total = unit_price * quantity
    
    return {
        "status": "completed",
        "item_code": item_code,
        "quantity": quantity,
        "customer_tier": customer_tier,
        "total_quote": total,
        "download_url": f"https://storage.erp.internal/quotes/QUOTE-{item_code}-{int(time.time())}.pdf"
    }