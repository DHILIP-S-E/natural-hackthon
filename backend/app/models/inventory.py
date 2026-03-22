"""Inventory models — product stock tracking and usage analytics."""
from sqlalchemy import String, Boolean, ForeignKey, Integer, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class InventoryItem(Base, TimestampMixin):
    __tablename__ = "inventory_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    location_id: Mapped[str] = mapped_column(String(36), ForeignKey("locations.id"), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_sku: Mapped[str | None] = mapped_column(String(100))
    category: Mapped[str | None] = mapped_column(String(100))
    brand: Mapped[str | None] = mapped_column(String(255))
    unit_of_measure: Mapped[str | None] = mapped_column(String(20))
    current_stock: Mapped[float | None] = mapped_column(Numeric(10, 2))
    reorder_level: Mapped[float | None] = mapped_column(Numeric(10, 2))
    reorder_quantity: Mapped[float | None] = mapped_column(Numeric(10, 2))
    cost_per_unit: Mapped[float | None] = mapped_column(Numeric(10, 2))
    last_reorder_date: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    average_daily_usage: Mapped[float | None] = mapped_column(Numeric(10, 2))
    days_until_stockout: Mapped[int | None] = mapped_column(Integer)
    linked_services: Mapped[list | None] = mapped_column(JSON)
    linked_trend_ids: Mapped[list | None] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<InventoryItem {self.product_name} stock={self.current_stock}>"


class InventoryUsageLog(Base, TimestampMixin):
    __tablename__ = "inventory_usage_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    inventory_item_id: Mapped[str] = mapped_column(String(36), ForeignKey("inventory_items.id"), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("service_sessions.id"))
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"))
    stylist_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("staff_profiles.id"))
    quantity_used: Mapped[float | None] = mapped_column(Numeric(10, 2))
    usage_type: Mapped[str | None] = mapped_column(String(50))
    quality_score_of_service: Mapped[float | None] = mapped_column(Numeric(4, 2))

    def __repr__(self) -> str:
        return f"<InventoryUsageLog item={self.inventory_item_id} qty={self.quantity_used}>"
