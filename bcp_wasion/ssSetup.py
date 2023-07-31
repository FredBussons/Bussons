import sqlite3
import sys
import csv
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QTimer

class setupAdmin(QWidget):
    def __init__(self, open_action=None):
        super().__init__()
        self.success_message_timer = None
        self.setWindowTitle("Cadastro de Setup")
        self.setGeometry(600, 200, 700, 700)
        self.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/logo-wasion.png"))
        self.setStyleSheet("background-color: blue")

        # Cria um widget central para a janela principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout vertical para o widget central
        layout = QVBoxLayout(central_widget)

        # Exemplo de conteúdo (um label para demonstrar o autoajuste de tela)
        label = QLabel("Exemplo de conteúdo autoajustável.")
        layout.addWidget(label)

    def showEvent(self, event):
        # Quando a janela é mostrada, maximiza ela automaticamente
        self.showMaximized()
        event.accept()

        self.setup_ui()

        self.csv_file = ""
        self.modelo_anterior = ""

        # Conexão com o banco de dados
        self.conn = sqlite3.connect('modelo.db')
        self.cursor = self.conn.cursor()

        # Cria a tabela modelos se não existir
        self.create_table_modelos()

    def create_table_modelos(self):
        # Cria a tabela "modelos" com os campos especificados
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS modelos (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        modelo TEXT NOT NULL,
                                        maquina TEXT NOT NULL,
                                        portal TEXT NOT NULL,
                                        posicao TEXT NOT NULL,
                                        divisao TEXT NOT NULL,
                                        codigo1 TEXT NOT NULL,
                                        codigo_alternativo TEXT NOT NULL
                                    )''')
        self.conn.commit()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.modelo_edit = QLineEdit()
        self.modelo_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.modelo_edit.setFont(QFont("Times", 20))
        self.add_field(layout, "Modelo:", self.modelo_edit)

        self.maquina_edit = QLineEdit()
        self.maquina_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.maquina_edit.setFont(QFont("Times", 20))
        self.maquina_edit.setMaxLength(3)
        self.maquina_edit.textChanged.connect(self.on_maquina_changed)
        self.add_field(layout, "Máquina:", self.maquina_edit)

        self.portal_edit = QLineEdit()
        self.portal_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.portal_edit.setFont(QFont("Times", 20))
        self.portal_edit.setMaxLength(1)
        self.portal_edit.textChanged.connect(self.on_portal_changed)
        self.add_field(layout, "Portal:", self.portal_edit)

        self.posicao_edit = QLineEdit()
        self.posicao_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.posicao_edit.setFont(QFont("Times", 20))
        self.posicao_edit.setMaxLength(2)
        self.posicao_edit.textChanged.connect(self.on_posicao_changed)
        self.add_field(layout, "Posição:", self.posicao_edit)

        self.divisao_edit = QLineEdit()
        self.divisao_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.divisao_edit.setFont(QFont("Times", 20))
        self.divisao_edit.setMaxLength(4)
        self.divisao_edit.textChanged.connect(self.on_divisao_changed)
        self.add_field(layout, "Divisão:", self.divisao_edit)

        self.codigo1_edit = QLineEdit()
        self.codigo1_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.codigo1_edit.setFont(QFont("Times", 20))
        self.codigo1_edit.textChanged.connect(self.on_codigo_changed)
        self.codigo1_edit.setMaxLength(15)
        self.add_field(layout, "Código:", self.codigo1_edit)

        self.codigo_alt_edit = QLineEdit()
        self.codigo_alt_edit.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.codigo_alt_edit.setFont(QFont("Times", 20))
        self.codigo_alt_edit.setMaxLength(15)
        self.codigo_alt_edit.textChanged.connect(self.on_codigo_alt_changed)
        self.add_field(layout, "Código Alternativo:", self.codigo_alt_edit)

        button_layout = QHBoxLayout()  # Novo layout para os botões
        self.cadastrar_button = QPushButton("Cadastrar")
        self.cadastrar_button.setFont(QFont("Times", 20))
        self.cadastrar_button.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.cadastrar_button.clicked.connect(self.cadastrar)
        self.cadastrar_button.setDefault(True)

        self.finalizar_button = QPushButton("Finalizar")
        self.finalizar_button.setFont(QFont("Times", 20))
        self.finalizar_button.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.finalizar_button.clicked.connect(self.finalizar)
        self.finalizar_button.clicked.connect(self.close)

        button_layout.addWidget(self.cadastrar_button)
        button_layout.addWidget(self.finalizar_button)

        layout.addLayout(button_layout)  # Adiciona o novo layout de botões ao layout principal

        self.table_widget = QTableWidget(self)  # Cria um widget de tabela
        layout.addWidget(self.table_widget)  # Adiciona o widget de tabela ao layout principal

        self.setLayout(layout)

    def add_field(self, layout, label_text, edit_widget):
        label = QLabel(label_text)
        label.setStyleSheet("color: white;")
        label.setFont(QFont("Times", 20))
        layout.addWidget(label)
        layout.addWidget(edit_widget)

    def on_maquina_changed(self, text):
        if len(text) == 3:
            self.portal_edit.setFocus()

    def on_portal_changed(self, text):
        if len(text) == 1:
            self.posicao_edit.setFocus()

    def on_posicao_changed(self, text):
        if len(text) == 2:
            self.divisao_edit.setFocus()

    def on_divisao_changed(self, text):
        if len(text) == 4:
            self.codigo1_edit.setFocus()

    def on_codigo_changed(self, text):
        if len(text) == 15:
            self.codigo_alt_edit.setFocus()

    def on_codigo_alt_changed(self, text):
        if len(text) == 15:
            self.cadastrar()  # Chama a função de cadastrar automaticamente quando o campo "Código Alternativo" é preenchido

    def cadastrar(self):
        # Verificar campos obrigatórios
        campos_obrigatorios = [
            self.modelo_edit.text(),
            self.maquina_edit.text(),
            self.portal_edit.text(),
            self.posicao_edit.text(),
            self.divisao_edit.text(),
            self.codigo1_edit.text(),
            self.codigo_alt_edit.text()
        ]

        if not all(campos_obrigatorios):
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: yellow; color: white; }")
            msg_box.setWindowTitle("Alerta")
            msg_box.setText("Todos os campos são obrigatórios")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.exec()
            return

        # Obter os dados dos campos
        modelo = self.modelo_edit.text()
        maquina = self.maquina_edit.text()
        portal = self.portal_edit.text()
        posicao = self.posicao_edit.text()
        divisao = self.divisao_edit.text()
        codigo1 = self.codigo1_edit.text()
        codigo_alt = self.codigo_alt_edit.text()

        # Definir o nome do arquivo CSV com base no valor do campo "Modelo"
        self.csv_file = f"{modelo}.csv"

        try:
            # Verificar se o código já existe no arquivo CSV
            if self.code_exists(codigo1, portal, posicao, divisao):
                raise Exception("Código já existe no banco de dados")

            # Adicionar os dados ao arquivo CSV
            with open(self.csv_file, mode="a", newline='') as file:
                writer = csv.writer(file)

                # Verificar se o arquivo CSV está vazio para adicionar o cabeçalho
                if file.tell() == 0:
                    header = ["Modelo", "Maquina", "Portal", "Posicao", "Divisao", "Codigo1", "Codigo Alternativo"]
                    writer.writerow(header)

                writer.writerow([modelo, maquina, portal, posicao, divisao, codigo1, codigo_alt])

            # Limpar todos os campos após cadastrar
            self.maquina_edit.clear()
            self.portal_edit.clear()
            self.posicao_edit.clear()
            self.divisao_edit.clear()
            self.codigo1_edit.clear()
            self.codigo_alt_edit.clear()

            # Exibir caixa de mensagem de cadastro realizado
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: green; color: white; }")
            msg_box.setWindowTitle("Sucesso")
            msg_box.setText("Código cadastrado com sucesso.")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("thumbs-up.svg"))

            # Remover botão "OK" e tornar a mensagem permanente
            msg_box.setStandardButtons(QMessageBox.NoButton)
            self.success_msg_box = msg_box  # Armazena a referência à caixa de mensagem

            msg_box.show()  # Exibe a caixa de mensagem

            # Agendar a função para fechar a caixa de mensagem após 3 segundos (3000 milissegundos)
            QTimer.singleShot(3000, self.close_success_message)

        except Exception as e:
            # Exibir caixa de mensagem de erro com botão "OK"
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: red; color: white; }")
            msg_box.setWindowTitle("Erro")
            msg_box.setText(str(e))  # Mostra a mensagem de erro
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

    def close_success_message(self):
        if self.success_msg_box is not None:
            self.success_msg_box.close()
            self.success_msg_box = None

        self.maquina_edit.setFocus()  # Move o cursor para o campo "Máquina"

        # Configurar o temporizador para fechar automaticamente após 5 segundos
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.msg_box.accept)
        timer.start(5000)

        self.maquina_edit.setFocus()  # Move o cursor para o campo "Máquina"

    def code_exists(self, codigo1, portal, posicao, divisao):
        # Verificar se o código já existe no arquivo CSV
        try:
            with open(self.csv_file, mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[5] == codigo1 and row[2] == portal and row[3] == posicao and row[4] == divisao:
                        return True
        except FileNotFoundError:
            return False

        return False

    def finalizar(self):
        try:
            # Verificar se o arquivo CSV foi criado
            if not self.csv_file:
                raise Exception("Você precisa cadastrar pelo menos um código antes de finalizar.")

            # Verificar se a tabela "modelos" está vazia
            if self.is_modelos_table_empty:
                raise Exception("Você precisa cadastrar pelo menos um código antes de finalizar.")

            # Exibir caixa de mensagem de sucesso ao finalizar
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: green; color: white; }")
            msg_box.setWindowTitle("Sucesso")
            msg_box.setText("Cadastro finalizado. Arquivo CSV exportado e modelos cadastrados no banco de dados.")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("thumbs-up.svg"))
            msg_box.exec()

        except Exception as e:
            # Exibir caixa de mensagem de erro com botão "OK"
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: red; color: white; }")
            msg_box.setWindowTitle("Erro")
            msg_box.setText(str(e))  # Mostra a mensagem de erro
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        # Fecha a janela após a finalização
        self.close()

    @property
    def is_modelos_table_empty(self):
    # Verifica se a tabela "modelos" está vazia
    self.cursor.execute("SELECT COUNT(*) FROM modelos")
    count = self.cursor.fetchone()[0]
        return count == 0

        except FileNotFoundError:
            # Exibe mensagem de erro se o arquivo CSV não for encontrado
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: red; color: white; }")
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Arquivo CSV não encontrado.")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.exec()

        # Fecha a janela após a finalização
            self.close()

    def update_table(self):
        # Atualiza a tabela no widget de visualização com os dados do banco de dados
        self.cursor.execute("SELECT * FROM modelos")
        data = self.cursor.fetchall()

        self.table_widget.clear()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Modelo", "Maquina", "Portal", "Posicao", "Divisao", "Codigo1", "Alternativo"])
        self.table_widget.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data[1:]):
                item = QTableWidgetItem(str(cell_data))
                self.table_widget.setItem(row_idx, col_idx, item)

    def importar_csv_para_banco(self):
        # Importar o arquivo CSV gerado para dentro do banco de dados
        try:
            with open(self.csv_file, mode="r") as file:
                reader = csv.reader(file)
                modelos = set(
                    [row[0] for row in reader])  # Extrai todos os modelos do arquivo CSV e remove duplicatas

            if modelos:
                # Insere os modelos na tabela "modelos"
                self.cursor.executemany('INSERT INTO modelos (modelo, maquina, portal, posicao, divisao, codigo1, alternativo) VALUES (?, ?, ?, ?, ?, ?, ?)',
                                        [(modelo, self.maquina_edit.text(), self.portal_edit.text(), self.posicao_edit.text(), self.divisao_edit.text(), self.codigo1_edit.text(), self.codigo_alt_edit.text()) for modelo in modelos])
                self.conn.commit()

                # Exibe mensagem de sucesso ao importar
                msg_box = QMessageBox()
                msg_box.setStyleSheet("QMessageBox { background-color: green; color: white; }")
                msg_box.setWindowTitle("Sucesso")
                msg_box.setText("Arquivo CSV importado e modelos cadastrados com sucesso.")
                msg_box.setFont(QFont("Times", 20))
                msg_box.setWindowIcon(QIcon("thumbs-up.svg"))
                msg_box.exec()

                # Atualiza a tabela no widget de visualização
                self.update_table()
            else:
                # Exibe mensagem de aviso se o arquivo CSV estiver vazio
                msg_box = QMessageBox()
                msg_box.setStyleSheet("QMessageBox { background-color: yellow; color: white; }")
                msg_box.setWindowTitle("Aviso")
                msg_box.setText("O arquivo CSV está vazio. Nenhum modelo foi cadastrado.")
                msg_box.setFont(QFont("Times", 20))
                msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
                msg_box.exec()

        except FileNotFoundError:
            # Exibe mensagem de erro se o arquivo CSV não for encontrado
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: red; color: white; }")
            msg_box.setWindowTitle("Erro")
            msg_box.setText("Arquivo CSV não encontrado.")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.exec()

        # Fecha a janela após a importação
        self.close()

    def setCentralWidget(self, central_widget):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = setupAdmin()
    window.show()
    sys.exit(app.exec_())
