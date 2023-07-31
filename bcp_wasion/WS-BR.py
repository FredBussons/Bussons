import sys
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from cFuncionarios import funcionarioAdmin
from cSetup import setupAdmin
from cAlimentacao import fAlimentacao

class menuPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Menu Principal")
        self.setFont(QFont("Times", 25))
        self.setGeometry(400, 40, 700, 700)
        self.setWindowIcon(QIcon("C://Users/fredi/PycharmProjects/pythonProject/logo-wasion.png"))
        self.setStyleSheet("background-color: blue")

        # Configuração da janela principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Layout vertical para o widget central
        layout = QVBoxLayout(central_widget)

    def showEvent(self, event):
        # Quando a janela é mostrada, maximiza ela automaticamente
        self.showMaximized()
        event.accept()

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()


        self.btn_setup = QPushButton("Cadastro de Setup", self)
        self.btn_setup.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.btn_setup.setFont(QFont("Times", 25))
        self.btn_setup.clicked.connect(self.cadastro_setup)
        layout.addWidget(self.btn_setup)

        self.btn_funcionario = QPushButton("Cadastro de Funcionário", self)
        self.btn_funcionario.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.btn_funcionario.setFont(QFont("Times", 25))
        self.btn_funcionario.clicked.connect(self.cadastro_funcionario)
        layout.addWidget(self.btn_funcionario)

        self.btn_alimentacao = QPushButton("Registro de Alimentação", self)
        self.btn_alimentacao.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.btn_alimentacao.setFont(QFont("Times", 25))
        self.btn_alimentacao.clicked.connect(self.registro_alimentacao)
        layout.addWidget(self.btn_alimentacao)

        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.setStyleSheet("background-color: green; color: white; border-radius: 10px;")
        self.btn_fechar.setFont(QFont("Times", 25))
        self.btn_fechar.clicked.connect(self.close)
        layout.addWidget(self.btn_fechar)

        self.central_widget.setLayout(layout)

    def cadastro_setup(self):
        self.btn_setup = setupAdmin()
        self.btn_setup.show()
        self.hide()

    def cadastro_funcionario(self):
        self.btn_funcionario = funcionarioAdmin()
        self.btn_funcionario.show()
        self.hide()

    def registro_alimentacao(self):
        self.btn_alimentacao = fAlimentacao()
        self.btn_alimentacao.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = menuPrincipal()
    window.show()
    sys.exit(app.exec())
