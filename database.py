import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Carrega a URL do banco de dados do arquivo .env ou variável de ambiente
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://usuario:senha@localhost:5432/controle")

# Função para conectar ao banco de dados PostgreSQL
def get_connection(dbname=None):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=dbname if dbname else os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para criar o banco de dados 'controle'
def create_database():
    try:
        # Conectando ao banco padrão 'postgres' para criar o banco 'controle'
        with get_connection('postgres') as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                # Verificar se o banco de dados já existe
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'controle';")
                exists = cursor.fetchone()

                if not exists:
                    cursor.execute(sql.SQL("CREATE DATABASE controle;"))
                    print("Banco de dados 'controle' criado com sucesso!")
                else:
                    print("O banco de dados 'controle' já existe.")
    except Exception as e:
        print(f"Erro ao criar o banco de dados: {e}")

# Função para criar a tabela 'producao'
def create_tables():
    try:
        # Conectando ao banco de dados 'controle'
        with get_connection('controle') as connection:
            with connection.cursor() as cursor:
                create_table_query = '''
                CREATE TABLE IF NOT EXISTS producao (
                    op VARCHAR(50) PRIMARY KEY,
                    descricao VARCHAR(255),
                    resina VARCHAR(100),
                    maquina VARCHAR(100),
                    peso_g FLOAT,
                    meta_hora INTEGER,
                    qtd_op INTEGER,
                    pecas_produzidas INTEGER DEFAULT 0,
                    pecas_rejeitadas INTEGER DEFAULT 0,
                    pecas_boas INTEGER DEFAULT 0,
                    saldo_produzir INTEGER DEFAULT 0,
                    fpy FLOAT DEFAULT 0.0,
                    preco_unitario FLOAT DEFAULT 0.01,
                    valor_total FLOAT DEFAULT 0.0,
                    situacao VARCHAR(50) DEFAULT 'Pendente',
                    data DATE DEFAULT CURRENT_DATE,
                    hora TIME DEFAULT CURRENT_TIME
                );
                '''
                cursor.execute(create_table_query)
                connection.commit()
                print("Tabela 'producao' criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar a tabela: {e}")

def salvar_dado_op(op_data):
    try:
        # Conectando ao banco de dados 'controle'
        with get_connection('controle') as connection:
            with connection.cursor() as cursor:
                # Verifica se a OP já existe
                cursor.execute("SELECT op FROM producao WHERE op = %s;", (op_data['op'],))
                registro_existente = cursor.fetchone()

                if registro_existente:
                    # Atualiza o registro existente (incrementa peças boas e decrementa saldo a produzir)
                    update_query = '''
                    UPDATE producao
                    SET pecas_boas = pecas_boas + 1,  -- Incrementa uma peça boa
                        pecas_produzidas = pecas_produzidas + 1,
                        saldo_produzir = saldo_produzir - 1,  -- Decrementa saldo a produzir
                        fpy = (pecas_boas / qtd_op) * 100
                    WHERE op = %s;
                    '''
                    cursor.execute(update_query, (op_data['op'],))
                    print(f"OP {op_data['op']} atualizada com sucesso.")
                else:
                    # Insere um novo registro se a OP não existir
                    insert_query = '''
                    INSERT INTO producao (op, descricao, resina, maquina, peso_g, meta_hora, qtd_op, 
                                          pecas_boas, pecas_produzidas, saldo_produzir, fpy, situacao, data, hora)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 1, %s, 0, 'Em Progresso', CURRENT_DATE, CURRENT_TIME);
                    '''
                    cursor.execute(insert_query, (
                        op_data['op'], op_data['descricao'], op_data['resina'], op_data['maquina'],
                        op_data['peso_g'], op_data['meta_hora'], op_data['qtd_op'],
                        op_data['saldo_produzir'] - 1  # Decrementa saldo ao inserir novo registro
                    ))
                    print(f"OP {op_data['op']} inserida com sucesso.")

                # Confirmar a transação
                connection.commit()

    except Exception as e:
        print(f"Erro ao salvar os dados no banco de dados: {e}")
