from contextlib import closing
from database import get_connection
from schemas import OPCreation
from openpyxl import Workbook
from io import BytesIO
from fastapi.responses import StreamingResponse

# Função para criar uma nova OP com uso de "with" para conexões
def create_op(op_data: OPCreation):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                query = """
                    INSERT INTO producao (op, descricao, resina, maquina, peso_g, meta_hora, qtd_op, saldo_produzir, preco_unitario, situacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pendente')
                    RETURNING *;
                """
                cursor.execute(query, (
                    op_data.op, op_data.descricao, op_data.resina, 
                    op_data.maquina, op_data.peso_g, op_data.meta_hora, 
                    op_data.qtd_op, op_data.qtd_op, op_data.preco_unitario
                ))
                op = cursor.fetchone()
                conn.commit()
                return op
            except Exception as e:
                conn.rollback()
                print(f"Erro ao criar a OP: {e}")
                raise  # Relança a exceção para tratamento superior

# Função para verificar se uma OP já existe
def get_op(op_id: str):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM producao WHERE op = %s;", (op_id,))
                return cursor.fetchone()  # Retorna todos os campos da tabela 'producao'
            except Exception as e:
                print(f"Erro ao buscar a OP {op_id}: {e}")
                return None

# Função para obter todas as OPs
def get_all_ops():
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM producao;")
                ops = cursor.fetchall()
                return ops
            except Exception as e:
                print(f"Erro ao buscar todas as OPs: {e}")
                return []


# Função para atualizar a produção
def update_producao(op_id: str, pecas_boas: int, pecas_rejeitadas: int):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                query = """
                    UPDATE producao 
                    SET pecas_boas = pecas_boas + %s, 
                        pecas_rejeitadas = pecas_rejeitadas + %s, 
                        saldo_produzir = saldo_produzir - %s,
                        fpy = CASE 
                                WHEN (pecas_boas + pecas_rejeitadas) > 0 
                                THEN (pecas_boas::float / (pecas_boas + pecas_rejeitadas)) * 100
                                ELSE 0
                             END
                    WHERE op = %s
                    RETURNING *;
                """
                cursor.execute(query, (pecas_boas, pecas_rejeitadas, pecas_boas, op_id))
                updated_op = cursor.fetchone()
                conn.commit()
                return updated_op
            except Exception as e:
                conn.rollback()
                print(f"Erro ao atualizar a produção da OP {op_id}: {e}")
                return None

# Função para excluir uma OP
def delete_op(op):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("DELETE FROM producao WHERE op = %s", (op,))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Erro ao excluir a OP {op}: {e}")

# Função para atualizar uma OP
def update_op(op, descricao, resina, maquina):
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("""
                    UPDATE producao
                    SET descricao = %s, resina = %s, maquina = %s
                    WHERE op = %s
                """, (descricao, resina, maquina, op))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Erro ao atualizar a OP {op}: {e}")

# Função para exportar o banco de dados para Excel com StreamingResponse
def export_database_to_excel():
    # Criar um novo arquivo Excel em memória
    output = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Producao"

    # Cabeçalhos
    headers = ["OP", "Descrição", "Resina", "Máquina", "Peso (g)", "Meta Hora", "Qtd OP", 
               "Peças Produzidas", "Peças Rejeitadas", "Peças Boas", "Saldo a Produzir", 
               "FPY (%)", "Preço Unitário", "Valor Total", "Situação", "Data", "Hora"]
    sheet.append(headers)

    # Obter os dados da tabela de produção
    ops = get_all_ops()

    # Escrever os dados na planilha
    for op in ops:
        sheet.append([
            op['op'], op['descricao'], op['resina'], op['maquina'], op['peso_g'], 
            op['meta_hora'], op['qtd_op'], op['pecas_produzidas'], 
            op['pecas_rejeitadas'], op['pecas_boas'], op['saldo_produzir'], 
            op['fpy'], op['preco_unitario'], op['valor_total'], 
            op['situacao'], op['data'], op['hora']
        ])

    # Ajustar a largura das colunas
    for col in sheet.columns:
        max_length = 0
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[col[0].column_letter].width = adjusted_width

    # Salvar o workbook no arquivo de memória
    workbook.save(output)
    output.seek(0)  # Reposicionar o ponteiro no início do arquivo de memória

    # Retornar o arquivo em memória via StreamingResponse
    headers = {
        'Content-Disposition': 'attachment; filename="banco_de_dados.xlsx"'
    }
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

def reset_producao_op(op_id: str):
    """
    Reseta os campos de produção (pecas_produzidas, pecas_rejeitadas, pecas_boas) para zero,
    mantendo o saldo a produzir inalterado.
    """
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                # Resetar os campos de produção, mantendo o saldo a produzir
                query = """
                    UPDATE producao
                    SET pecas_produzidas = 0,
                        pecas_rejeitadas = 0,
                        pecas_boas = 0
                    WHERE op = %s
                    RETURNING *;
                """
                cursor.execute(query, (op_id,))
                op_atualizada = cursor.fetchone()
                conn.commit()
                return op_atualizada
            except Exception as e:
                conn.rollback()
                print(f"Erro ao resetar a produção da OP {op_id}: {e}")
                return None
def reset_producao_op(op_id: str):
    """
    Reseta os campos de produção (pecas_produzidas, pecas_rejeitadas, pecas_boas) para zero,
    mantendo o saldo a produzir inalterado.
    """
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                # Resetar os campos de produção, mantendo o saldo a produzir
                query = """
                    UPDATE producao
                    SET pecas_produzidas = 0,
                        pecas_rejeitadas = 0,
                        pecas_boas = 0
                    WHERE op = %s
                    RETURNING *;
                """
                cursor.execute(query, (op_id,))
                op_atualizada = cursor.fetchone()
                conn.commit()
                return op_atualizada
            except Exception as e:
                conn.rollback()
                print(f"Erro ao resetar a produção da OP {op_id}: {e}")
                return None