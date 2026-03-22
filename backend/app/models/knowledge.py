"""KnowledgeBaseEntry model — staff-contributed tips and insights (PS-02.06)."""
from sqlalchemy import String, Boolean, ForeignKey, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base, TimestampMixin, generate_uuid


class KnowledgeBaseEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_base_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    staff_id: Mapped[str] = mapped_column(String(36), ForeignKey("staff_profiles.id"), nullable=False)
    knowledge_type: Mapped[str | None] = mapped_column(String(50))  # product_tip, service_combo, customer_insight
    service_category: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list | None] = mapped_column(JSON)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    upvotes: Mapped[int] = mapped_column(default=0)

    def __repr__(self) -> str:
        return f"<KnowledgeBaseEntry {self.knowledge_type}: {self.title}>"
