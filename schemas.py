from pydantic import BaseModel, Field

class OPCreation(BaseModel):
    op: str = Field(..., title="Número da OP", max_length=50)
    descricao: str = Field(..., title="Descrição da OP", max_length=255)
    resina: str = Field(..., title="Tipo de Resina", max_length=100)
    maquina: str = Field(..., title="Máquina", max_length=100)
    peso_g: float = Field(..., title="Peso em Gramas", gt=0, description="Peso do produto em gramas")
    meta_hora: int = Field(..., title="Meta por Hora", gt=0, description="Meta de produção por hora")
    qtd_op: int = Field(..., title="Quantidade de OP", gt=0, description="Quantidade total da OP")
    preco_unitario: float = Field(..., title="Preço Unitário", gt=0, description="Preço unitário do produto")

    class Config:
        # Pode ser removido se não for usado para ORM
        json_schema_extra = {
            "example": {
                "op": "OP001",
                "descricao": "Produção de peças plásticas",
                "resina": "Polietileno",
                "maquina": "Máquina A",
                "peso_g": 120.5,
                "meta_hora": 100,
                "qtd_op": 1000,
                "preco_unitario": 1.5
            }
        }

class OPView(OPCreation):
    pecas_produzidas: int = Field(0, title="Peças Produzidas", ge=0, description="Número de peças produzidas")
    pecas_rejeitadas: int = Field(0, title="Peças Rejeitadas", ge=0, description="Número de peças rejeitadas")
    pecas_boas: int = Field(0, title="Peças Boas", ge=0, description="Número de peças boas")
    saldo_produzir: int = Field(0, title="Saldo a Produzir", ge=0, description="Saldo de peças a serem produzidas")
    fpy: float = Field(0.0, title="First Pass Yield (FPY)", ge=0, le=100, description="Porcentagem FPY")
    valor_total: float = Field(0.0, title="Valor Total", ge=0, description="Valor total acumulado da OP")
    situacao: str = Field("Pendente", title="Situação", max_length=50, description="Situação da OP")

    class Config:
        # Pode ser removido se não for usado para ORM
        json_schema_extra = {
            "example": {
                "op": "OP001",
                "descricao": "Produção de peças plásticas",
                "resina": "Polietileno",
                "maquina": "Máquina A",
                "peso_g": 120.5,
                "meta_hora": 100,
                "qtd_op": 1000,
                "preco_unitario": 1.5,
                "pecas_produzidas": 500,
                "pecas_rejeitadas": 20,
                "pecas_boas": 480,
                "saldo_produzir": 500,
                "fpy": 96.0,
                "valor_total": 720.0,
                "situacao": "Em Progresso"
            }
        }