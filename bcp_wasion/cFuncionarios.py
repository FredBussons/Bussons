import sys
import sqlite3
import csv
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QIcon, QKeyEvent, QFont, QGuiApplication
from PySide6.QtCore import Qt


class funcionarioAdmin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cadastro de Funcionários")
        self.setGeometry(600, 200, 700, 700)
        self.setWindowIcon(QIcon('C:/Users/fredi/PycharmProjects/pythonProject/logo-wasion.png'))
        self.setStyleSheet("background-color: blue; border-radius:10x;")

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

        # Conexão com o banco de dados
        self.conn = sqlite3.connect('funcionario.db')
        self.cursor = self.conn.cursor()

        # Cria a tabela funcionarios se não existir
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome TEXT NOT NULL,
                                turno TEXT NOT NULL,
                                matricula TEXT NOT NULL
                            )''')
        self.conn.commit()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Label e campo de entrada para o nome
        lbl_nome = QLabel("Funcionário:")
        lbl_nome.setStyleSheet("color: white;")
        lbl_nome.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_nome = QLineEdit()
        self.txt_nome.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.txt_nome.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_nome.setPlaceholderText("Digite o nome do funcionário")
        layout.addWidget(lbl_nome)
        layout.addWidget(self.txt_nome)

        # Label e campo de entrada para o turno
        lbl_turno = QLabel("Turno:")
        lbl_turno.setStyleSheet("color: white;")
        lbl_turno.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_turno = QLineEdit()
        self.txt_turno.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.txt_turno.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_turno.setPlaceholderText("Digite o turno do funcionário")
        layout.addWidget(lbl_turno)
        layout.addWidget(self.txt_turno)

        # Label e campo de entrada para a matrícula
        lbl_matricula = QLabel("Matrícula:")
        lbl_matricula.setStyleSheet("color: white;")
        lbl_matricula.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_matricula = QLineEdit()
        self.txt_matricula.setStyleSheet("background-color: white; color: black; border-radius: 10px;")
        self.txt_matricula.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        self.txt_matricula.setPlaceholderText("Digite a matrícula do funcionário")
        layout.addWidget(lbl_matricula)
        layout.addWidget(self.txt_matricula)

        # Define o estilo para as QLineEdit brancas
        style_sheet_line_edit = "QLineEdit { background-color: white; }"
        self.txt_nome.setStyleSheet(style_sheet_line_edit)
        self.txt_turno.setStyleSheet(style_sheet_line_edit)
        self.txt_matricula.setStyleSheet(style_sheet_line_edit)



        # Layout horizontal para os botões
        layout_botoes = QHBoxLayout()

        # Botão para cadastrar o funcionário
        btn_cadastrar = QPushButton("Cadastrar")
        btn_cadastrar.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        btn_cadastrar.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        btn_cadastrar.clicked.connect(self.cadastrar_funcionario)
        layout_botoes.addWidget(btn_cadastrar)

        # Botão para finalizar e fechar a janela
        btn_finalizar = QPushButton("Voltar")
        btn_finalizar.setFont(QFont("Times", 20))  # Ajuste de tamanho da fonte
        btn_finalizar.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        btn_finalizar.clicked.connect(self.close)
        layout_botoes.addWidget(btn_finalizar)

        # Adiciona o layout dos botões ao layout principal
        layout.addLayout(layout_botoes)

        self.setLayout(layout)

    def cadastrar_funcionario(self):
        nome = self.txt_nome.text()
        turno = self.txt_turno.text()
        matricula = self.txt_matricula.text()

        # Verifica se todos os campos foram preenchidos
        if nome.strip() == '' or turno.strip() == '' or matricula.strip() == '':
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: yellow; color: white; }")
            msg_box.setWindowTitle("Alerta")
            msg_box.setText("Todos os campos são obrigatórios")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-down.svg"))
            msg_box.exec()
            return

        # Verifica se o funcionário já está cadastrado
        self.cursor.execute("SELECT * FROM funcionarios WHERE nome=?", (nome,))
        existente = self.cursor.fetchone()
        if existente:
            msg_box = QMessageBox()
            msg_box.setStyleSheet("QMessageBox { background-color: red; color: white; }")
            msg_box.setWindowTitle("Alerta")
            msg_box.setText("O funcionário já está cadastrado.")
            msg_box.setFont(QFont("Times", 20))
            msg_box.setWindowIcon(QIcon("logo/emoji-frown-fill.svg"))
            msg_box.exec()
            return

        # Insere o funcionário na tabela
        self.cursor.execute("INSERT INTO funcionarios (nome, turno, matricula) VALUES (?, ?, ?)",
                            (nome, turno, matricula))
        self.conn.commit()

        # Exibe uma mensagem de "Cadastrado com Sucesso"
        msg_box = QMessageBox()
        msg_box.setStyleSheet("QMessageBox { background-color: green; color: white; }")
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText("Funcionário cadastrado com sucesso.")
        msg_box.setFont(QFont("Times", 20))
        msg_box.setWindowIcon(QIcon("C:/Users/fredi/PycharmProjects/pythonProject/thumbs-up.svg"))
        msg_box.exec()

        # Limpa os campos de entrada
        self.txt_nome.clear()
        self.txt_turno.clear()
        self.txt_matricula.clear()
        self.txt_nome.setFocus()

        # Gera o arquivo CSV com os funcionários
        self.gerar_csv()

    def gerar_csv(self):
        # Seleciona todos os funcionários da tabela
        self.cursor.execute("SELECT * FROM funcionarios")
        funcionarios = self.cursor.fetchall()

        # Define o nome do arquivo CSV
        nome_arquivo = 'funcionarios.csv'

        # Gera o arquivo CSV
        with open(nome_arquivo, 'w', newline='') as arquivo_csv:
            writer = csv.writer(arquivo_csv, delimiter=',')
            # Escreve o cabeçalho
            writer.writerow(['Nome', 'Turno', 'Matrícula'])
            # Escreve os dados dos funcionários
            for funcionario in funcionarios:
                writer.writerow([funcionario[1], funcionario[2], funcionario[3]])

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.txt_nome.hasFocus():
                self.txt_turno.setFocus()
            elif self.txt_turno.hasFocus():
                self.txt_matricula.setFocus()
            elif self.txt_matricula.hasFocus():
                self.cadastrar_funcionario()

    def closeEvent(self, event):
        # Fecha a conexão com o banco de dados ao fechar a janela
        self.conn.close()

    def setCentralWidget(self, central_widget):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = funcionarioAdmin()
    window.show()
    sys.exit(app.exec())