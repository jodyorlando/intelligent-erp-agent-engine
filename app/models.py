from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Text, func, JSON
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="operator", nullable=False)  
    customer_tier = Column(String, default="standard", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    orders = relationship("DraftOrder", back_populates="user")
    agent_logs = relationship("AgentRunLog", back_populates="user")

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String, unique=True, index=True, nullable=False)
    item_name = Column(String, nullable=False)
    stock_qty = Column(Integer, default=0, nullable=False)
    unit_price = Column(Float, nullable=False)
    warehouse_location = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class DraftOrder(Base):
    __tablename__ = "draft_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)
    item_code = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="draft", nullable=False)  # draft, approved, rejected
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user = relationship("User", back_populates="orders")

class AgentRunLog(Base):
    __tablename__ = "agent_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)  # Stores list of tools executed and outputs
    final_response = Column(Text, nullable=True)
    status = Column(String, default="running", nullable=False)  # running, completed, failed
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user = relationship("User", back_populates="agent_logs")