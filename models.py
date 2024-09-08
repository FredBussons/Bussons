from sqlalchemy import Column, Integer, String, Float, Date, Time, func
from .database import Base

class Producao(Base):
    __tablename__ = "producao"
    
    op = Column(String, primary_key=True, index=True)
    descricao = Column(String)
    resina = Column(String)
    maquina = Column(String)
    peso_g = Column(Float)
    meta_hora = Column(Integer)
    qtd_op = Column(Integer)
    pecas_produzidas = Column(Integer, default=0)
    pecas_rejeitadas = Column(Integer, default=0)
    pecas_boas = Column(Integer, default=0)
    acumulado_turno = Column(Integer, default=0)
    saldo_produzir = Column(Integer)
    fpy = Column(Float, default=0.0)
    preco_unitario = Column(Float, default=0.01)
    valor_total = Column(Float, default=0.0)
    situacao = Column(String, default="Pendente")
    # Use CURRENT_DATE e CURRENT_TIME do PostgreSQL para definir data e hora
    data = Column(Date, server_default=func.current_date()) 
    hora = Column(Time, server_default=func.current_time())  
