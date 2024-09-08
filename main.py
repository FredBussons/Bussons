import asyncio
from io import BytesIO
from fastapi import FastAPI, HTTPException, Request, Form, Depends, APIRouter
from openpyxl import Workbook
from crud import create_op, get_all_ops, get_op, update_producao, delete_op, update_op, export_database_to_excel, reset_producao_op, get_connection
from schemas import OPCreation, OPView
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from database import create_database, create_tables
from arduino import ArduinoHandler
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from datetime import datetime
from pydantic import BaseModel
from database import salvar_dado_op



app = FastAPI()

# Carrega os templates da pasta "templates"
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicializar o ArduinoHandler
arduino = ArduinoHandler(port='COM1', baudrate=9600)

# Model para os dados de produção
class DadosProducao(BaseModel):
    op: str
    descricao: str
    resina: str
    maquina: str
    peso_g: float
    meta_hora: int
    qtd_op: int
    pecas_produzidas: int
    pecas_rejeitadas: int
    pecas_boas: int
    acumulado_turno: int
    saldo_produzir: int
    fpy: float
    qtd_cavidades: int
    preco_unitario: float
    valor_total: float
    situacao: str

# Exibe o menu principal
@app.get("/", response_class=HTMLResponse)
async def read_menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

# Exibe o formulário de cadastro de OP
@app.get("/cadastrar_op", response_class=HTMLResponse)
async def show_form(request: Request):
    return templates.TemplateResponse("cadastrar_op.html", {"request": request})

# Rota POST para processar o cadastro de OP
@app.post("/cadastrar_op", response_class=HTMLResponse)
async def cadastrar_op(
    request: Request,
    op: str = Form(...),
    descricao: str = Form(...),
    resina: str = Form(...),
    maquina: str = Form(...),
    peso_g: float = Form(...),
    meta_hora: int = Form(...),
    qtd_op: int = Form(...),
    preco_unitario: float = Form(...)
):
    # Verifica se a OP já está cadastrada no banco de dados
    existing_op = get_op(op)
    if existing_op:
        return templates.TemplateResponse(
            "cadastrar_op.html", 
            {"request": request, "message": f"Erro: A OP {op} já está cadastrada!"}
        )

    # Se a OP não existir, prossegue com o cadastro
    op_data = OPCreation(
        op=op, descricao=descricao, resina=resina, maquina=maquina, peso_g=peso_g,
        meta_hora=meta_hora, qtd_op=qtd_op, preco_unitario=preco_unitario
    )
    try:
        create_op(op_data)
        # Retornar o formulário com uma mensagem de sucesso
        return templates.TemplateResponse("cadastrar_op.html", {"request": request, "message": "Plano cadastrado com sucesso!"})
    except Exception as e:
        # Retornar o formulário com uma mensagem de erro
        return templates.TemplateResponse("cadastrar_op.html", {"request": request, "message": f"Erro ao cadastrar: {str(e)}"})

# Rota para criar uma nova OP via API
@app.post("/op/", response_model=OPView)
def create_op_route(op_data: OPCreation):
    op = create_op(op_data)
    if not op:
        raise HTTPException(status_code=400, detail="Erro ao criar OP")
    return op

# Rota para buscar todas as OPs
@app.get("/ops/", response_model=list[OPView])
def get_all_ops_route():
    ops = get_all_ops()
    return ops

# Rota para buscar uma OP específica
@app.get("/ops/{op_id}", response_model=OPView)
def get_op_route(op_id: str):
    op = get_op(op_id)
    if not op:
        raise HTTPException(status_code=404, detail="OP não encontrada")
    return op

# Rota para atualizar a produção de uma OP
@app.post("/op/{op_id}/producao/")
def update_producao_route(op_id: str, pecas_boas: int, pecas_rejeitadas: int):
    updated_op = update_producao(op_id, pecas_boas, pecas_rejeitadas)
    if not updated_op:
        raise HTTPException(status_code=404, detail="OP não encontrada ou erro ao atualizar")
    return updated_op

# Rota para exibir a página de banco de dados
@app.get("/banco_de_dados", response_class=HTMLResponse)
async def banco_de_dados(request: Request):
    ops = get_all_ops()  # Função que busca todos os dados da tabela 'producao'
    return templates.TemplateResponse("banco_de_dados.html", {"request": request, "ops": ops})

# Rota POST para salvar alterações de uma OP
@app.post("/banco_de_dados/salvar")
async def salvar_alteracoes(request: Request, op: str = Form(...), descricao: str = Form(...), resina: str = Form(...), maquina: str = Form(...)):
    try:
        update_op(op, descricao, resina, maquina)  # Função que atualiza os dados de uma OP
        return templates.TemplateResponse("banco_de_dados.html", {"request": request, "message": "Alterações salvas com sucesso!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rota POST para excluir uma OP
@app.post("/banco_de_dados/excluir")
async def excluir_op(request: Request, op: str = Form(...)):
    try:
        delete_op(op)  # Função que exclui uma OP do banco de dados
        return templates.TemplateResponse("banco_de_dados.html", {"request": request, "message": "OP excluída com sucesso!"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Definir a rota para exportação de banco de dados para Excel
@app.get("/banco_de_dados/exportar", response_class=StreamingResponse)
async def exportar_banco_de_dados():
    # Chamar a função de exportação definida no crud.py
    return export_database_to_excel()

# API para buscar todas as OPs no formato JSON
@app.get("/api/get_all_ops", response_class=JSONResponse)
async def api_get_all_ops():
    ops = get_all_ops()
    return ops

# Inicializar o banco de dados e as tabelas ao iniciar o app
@app.on_event("startup")
async def startup():
    create_database()  # Criar o banco de dados
    create_tables()    # Criar as tabelas necessárias

# Mensagem de status da API
@app.get("/status/")
async def root():
    return {"message": "Banco de dados configurado e API rodando!"}

from fastapi.responses import StreamingResponse
from io import BytesIO
from openpyxl import Workbook

@app.get("/banco_de_dados/exportar", response_class=StreamingResponse)
async def exportar_banco_de_dados():
    # Criar um arquivo Excel em memória
    output = BytesIO()
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Producao"

    # Cabeçalhos (ajustados conforme os campos do banco de dados)
    headers = ["OP", "Descrição", "Resina", "Máquina", "Peso (g)", "Meta Hora", "Qtd OP", 
               "Peças Produzidas", "Peças Rejeitadas", "Peças Boas", "Saldo a Produzir", 
               "FPY (%)", "Preço Unitário", "Valor Total", "Situação", "Data", "Hora"]
    sheet.append(headers)
    
    ops = get_all_ops()  
    for op in ops:
        sheet.append([
            op['op'],
            op['descricao'],
            op['resina'],
            op['maquina'],
            op['peso_g'],
            op['meta_hora'],
            op['qtd_op'],
            op['pecas_produzidas'],     
            op['pecas_rejeitadas'],
            op['pecas_boas'],
            op['saldo_produzir'],
            op['fpy'],
            op['preco_unitario'],
            op['valor_total'],            
            op['situacao'],
            op['data'],                  
            op['hora']                    
        ])

    workbook.save(output)
    output.seek(0) 

    headers = {
        'Content-Disposition': 'attachment; filename="banco_de_dados.xlsx"'
    }
    return StreamingResponse(output, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)

# Rota para servir o arquivo `producao.html`
@app.get("/producao")
async def producao_page(request: Request):
    return templates.TemplateResponse("producao.html", {"request": request})

@app.post("/iniciar_producao")
async def iniciar_producao(op: dict):
    op_id = op.get('op')

    # Buscar as informações da OP no banco de dados
    op_data = get_op(op_id)

    if not op_data:
        return {"status": "Erro", "message": f"OP {op_id} não encontrada"}

    # Verificar se o Arduino está conectado
    if not arduino.is_connected():
        if not arduino.connect():
            return {"status": "Erro", "message": "Não foi possível conectar ao Arduino"}

    # Lógica de contagem através do Arduino
    def contar_pecas_arduino():
        while arduino.is_connected():
            data = arduino.read_data()  # Ler dados do Arduino
            if data == 'OK1':  # Sinal de peça boa
                op_data['pecas_boas'] += 1
                op_data['pecas_produzidas'] += 1
            elif data == 'OK2':  # Sinal de peça rejeitada
                op_data['pecas_rejeitadas'] += 1
                op_data['pecas_produzidas'] += 1

            # Atualizar saldo a produzir e progresso
            op_data['saldo_produzir'] -= 1
            progresso = (op_data['pecas_boas'] / op_data['qtd_op']) * 100 if op_data['qtd_op'] > 0 else 0

            # Salvar automaticamente no banco de dados
            salvar_dados_no_banco(op_data)

            # Enviar dados atualizados para o front-end
            return {
                "status": "Conectado",
                "descricao": op_data.get('descricao', '---'),
                "resina": op_data.get('resina', '---'),
                "maquina": op_data.get('maquina', '---'),
                "peso_g": op_data.get('peso_g', 0.0),
                "meta_hora": op_data.get('meta_hora', 0),
                "qtd_op": op_data.get('qtd_op', 0),
                "pecasProduzidas": op_data.get('pecas_produzidas', 0),
                "pecasRejeitadas": op_data.get('pecas_rejeitadas', 0),
                "pecasBoas": op_data.get('pecas_boas', 0),
                "saldoProduzir": op_data.get('saldo_produzir', 0),
                "progresso": progresso
            }

    return contar_pecas_arduino()

    return contar_pecas_arduino()


    
@app.get("/op/{op_id}", response_class=JSONResponse)
async def buscar_op(op_id: str):
    op = get_op(op_id)
    if op:
        return op
    else:
        raise HTTPException(status_code=404, detail="OP não encontrada")

@app.websocket("/ws/contagem")
async def websocket_contagem(websocket: WebSocket):
    await websocket.accept()

    # Verifique se o Arduino está conectado
    if not arduino.is_connected():
        if not arduino.connect():
            await websocket.send_json({"status": "Erro", "message": "Não foi possível conectar ao Arduino"})
            await websocket.close()
            return

    try:
        # Continuamente ler os dados do Arduino e enviar ao cliente WebSocket
        while True:
            data = arduino.read_data()  # Ler os dados do Arduino
            if data:
                # Se o dado recebido for 'OK1', atualize o banco de dados
                if data == 'OK1':  # Incrementa peça boa
                    # Defina os dados da OP que precisam ser atualizados
                    op_data = {
                        "op": "2511",  # Certifique-se de passar o ID da OP correto
                        "descricao": "VENTILADOR DE PAREDE",
                        "resina": "PVC PRETA",
                        "maquina": "18",
                        "peso_g": 0.24,
                        "meta_hora": 1500,
                        "qtd_op": 18000,
                        "saldo_produzir": 17343  # Valor inicial do saldo a produzir (pode ser dinâmico)
                    }

                    # Chame a função para salvar no banco de dados
                    salvar_dado_op(op_data)  # Função que salva/incrementa peça boa

                    # Enviar a resposta de sucesso para o cliente WebSocket
                    await websocket.send_json({"status": "ok", "type": "OK1", "message": "Peça boa salva no banco de dados"})

                elif data == 'OK2':  # Incrementa peça rejeitada
                    await websocket.send_json({"status": "ok", "type": "OK2", "message": "Peça rejeitada recebida"})
                
                else:
                    await websocket.send_json({"status": "info", "message": f"Dado recebido: {data}"})

            await asyncio.sleep(0.5)  # Evita loop contínuo muito rápido

    except WebSocketDisconnect:
        print("Conexão WebSocket encerrada")
        await websocket.close()
        
@app.post("/parar_producao")
async def parar_producao():
    if arduino.is_connected():
        arduino.disconnect()  # Função que desconecta o Arduino
        return {"status": "Desconectado", "message": "Produção interrompida e Arduino desconectado"}
    else:
        return {"status": "Erro", "message": "O Arduino não estava conectado"}
    
from datetime import datetime

def salvar_dados_no_banco(op_data):
    try:
        # Conectando ao banco de dados 'controle'
        conn = get_connection('controle')
        if not conn:
            raise Exception("Não foi possível estabelecer conexão com o banco de dados.")
        
        with conn.cursor() as cursor:
            # Verifica se o preço unitário é válido
            if op_data.get('preco_unitario') is None or op_data.get('preco_unitario') <= 0:
                op_data['preco_unitario'] = 0.01  # Preço mínimo

            # Cálculo do valor total
            novo_valor_total = op_data['pecas_boas'] * op_data['preco_unitario']
            valor_total_atualizado = op_data['valor_total'] + novo_valor_total
            situacao = "Pendente"

            # Verifica se o registro já existe no banco de dados
            cursor.execute('SELECT op FROM producao WHERE op = %s', (op_data['op'],))
            registro_existente = cursor.fetchone()

            if registro_existente:
                # Atualiza o registro existente
                cursor.execute('''
                UPDATE producao SET
                    descricao = %s,
                    resina = %s,
                    maquina = %s,
                    peso_g = %s,
                    meta_hora = %s,
                    qtd_op = %s,
                    pecas_produzidas = %s,
                    pecas_rejeitadas = %s,
                    pecas_boas = %s,
                    saldo_produzir = %s,
                    fpy = %s,
                    preco_unitario = %s,
                    valor_total = %s,
                    situacao = %s,
                    data = %s,
                    hora = %s
                WHERE op = %s
                ''', (
                    op_data['descricao'],
                    op_data['resina'],
                    op_data['maquina'],
                    op_data['peso_g'],
                    op_data['meta_hora'],
                    op_data['qtd_op'],
                    op_data['pecas_produzidas'],
                    op_data['pecas_rejeitadas'],
                    op_data['pecas_boas'],
                    op_data['saldo_produzir'],
                    op_data['fpy'],
                    op_data['preco_unitario'],
                    valor_total_atualizado,
                    situacao,
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S"),
                    op_data['op']
                ))
            else:
                # Insere novo registro no banco de dados
                cursor.execute('''
                INSERT INTO producao (
                    op, descricao, resina, maquina, peso_g, meta_hora, qtd_op, pecas_produzidas,
                    pecas_rejeitadas, pecas_boas, saldo_produzir, fpy,
                    preco_unitario, valor_total, situacao, data, hora
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    op_data['op'],
                    op_data['descricao'],
                    op_data['resina'],
                    op_data['maquina'],
                    op_data['peso_g'],
                    op_data['meta_hora'],
                    op_data['qtd_op'],
                    op_data['pecas_produzidas'],
                    op_data['pecas_rejeitadas'],
                    op_data['pecas_boas'],
                    op_data['saldo_produzir'],
                    op_data['fpy'],
                    op_data['preco_unitario'],
                    valor_total_atualizado,
                    situacao,
                    datetime.now().strftime("%Y-%m-%d"),
                    datetime.now().strftime("%H:%M:%S")
                ))

            # Confirma a transação
            conn.commit()
            print(f"Dados da OP {op_data['op']} salvos com sucesso!")
            
    except Exception as e:
        print(f"Erro ao salvar os dados no banco de dados: {e}")
    finally:
        # Certifica-se de fechar a conexão após a operação
        if conn:
            conn.close()

@app.post("/resetar_op/{op_id}")
async def resetar_op(op_id: str):
    """
    Rota para resetar os campos de produção de uma OP (peças boas, rejeitadas, produzidas),
    mantendo o saldo a produzir inalterado.
    """
    # Chamar a função reset_producao_op do crud.py
    op_atualizada = reset_producao_op(op_id)

    if op_atualizada:
        return {"status": "sucesso", "op": op_atualizada}
    else:
        raise HTTPException(status_code=404, detail="OP não encontrada ou erro ao resetar")        