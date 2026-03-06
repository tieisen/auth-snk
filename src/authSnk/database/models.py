from datetime import datetime
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .database import Base

class Solucao(Base):
    __tablename__ = "solucao"
    __table_args__ = (
        CheckConstraint("ambiente IN ('prd', 'snd')", name='ck_ambiente'),
        UniqueConstraint("clientId","componente","ambiente", name="uq_solucao_client_comp_amb"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    descricao: Mapped[str] = mapped_column(String(50), nullable=False)
    componente: Mapped[str] = mapped_column(String(50), nullable=False)
    ambiente: Mapped[str] = mapped_column(String(3), nullable=False)
    clientId: Mapped[str] = mapped_column(String, nullable=False)
    clientSecret: Mapped[str] = mapped_column(String, nullable=False)
    xToken: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    token: Mapped[str] = mapped_column(String, nullable=True)
    dhGeracaoToken: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    dhExpiracaoToken: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    logs = relationship("Log", back_populates="solucoes", cascade="all, delete-orphan", passive_deletes=True)    

class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    dhRegistro: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    mensagem: Mapped[str] = mapped_column(String, nullable=True)
    solucao_id: Mapped[int] = mapped_column(Integer, ForeignKey("solucao.id", ondelete="CASCADE"), nullable=True)
    
    solucoes = relationship("Solucao", back_populates="logs")