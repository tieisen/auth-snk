from datetime import datetime, timezone, timedelta
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Solucao(Base):
    __tablename__ = "solucao"
    __table_args__ = (CheckConstraint("ambiente IN ('prd', 'snd')", name='ck_ambiente'),)    

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    descricao: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    componente: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ambiente: Mapped[str] = mapped_column(String(3), nullable=False)
    clientId: Mapped[str] = mapped_column(String, unique=True)
    clientSecret: Mapped[str] = mapped_column(String, unique=True)
    xToken: Mapped[str] = mapped_column(String, unique=True)
    token: Mapped[str] = mapped_column(String, nullable=True)
    dhGeracaoToken: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    dhExpiracaoToken: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    logs = relationship("Log", back_populates="solucoes", cascade="all, delete-orphan", passive_deletes=True)    

class Log(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dhRegistro: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=-3))))
    sucesso: Mapped[bool] = mapped_column(Boolean, default=False)
    mensagem: Mapped[str] = mapped_column(String, nullable=True)
    solucao_id: Mapped[int] = mapped_column(Integer, ForeignKey("solucao.id", ondelete="CASCADE"), nullable=True)
    
    solucoes = relationship("Solucao", back_populates="logs")    
    