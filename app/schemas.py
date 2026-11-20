from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

# --- Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    customer_tier: Optional[str] = "standard"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    customer_tier: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- ERP Inventory & Quote Schemas ---
class InventoryResponse(BaseModel):
    item_code: str
    item_name: str
    stock_qty: int
    unit_price: float
    warehouse_location: str

    model_config = ConfigDict(from_attributes=True)


class QuoteRequest(BaseModel):
    item_code: str
    quantity: int
    customer_tier: Optional[str] = "standard"


class QuoteResponse(BaseModel):
    item_code: str
    quantity_requested: int
    in_stock: bool
    stock_available: int
    unit_price: float
    discount_percent: int
    total_price: float

# --- Agent Processing Schemas ---
class AgentPromptRequest(BaseModel):
    prompt: str
    thread_id: Optional[str] = None


class AgentRunResponse(BaseModel):
    run_id: str
    prompt: str
    final_response: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    status: str

    model_config = ConfigDict(from_attributes=True)