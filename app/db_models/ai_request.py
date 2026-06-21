
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, DateTime, func, JSON, Integer, Float, Text
from datetime import datetime
from app.db.database import base


class AIRequest(base):

    __tablename__ = "ai_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    request_id: Mapped[int] = mapped_column(
        ForeignKey("requests.id", ondelete="CASCADE"),
        index=True
    )
    
    provider: Mapped[str] = mapped_column(
        String(50),
        index=True,
        comment="Provider: openai, anthropic, gemini, etc."
    )
    
    model: Mapped[str] = mapped_column(
        String(255),
        index=True,
        comment="Model identifier: gpt-4, claude-3-opus, etc."
    )
    
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of input tokens used"
    )
    
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of output tokens generated"
    )
    
    total_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Total tokens = input + output"
    )
    
    estimated_cost: Mapped[float] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated cost in USD for this request"
    )
    
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
        comment="Request latency in milliseconds"
    )
    
    usage_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Provider-specific metadata (cache_tokens, finish_reason, etc.)"
    )
    
    tags: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Array of tags: ['ai', 'openai', 'production', etc.]"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )


class AIProviderConfig(base):

    __tablename__ = "ai_provider_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    provider: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True
    )
    
    models: Mapped[dict] = mapped_column(
        JSON,
        comment="Model configurations: {model_name: {input_cost, output_cost, cache_input_cost}}"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
