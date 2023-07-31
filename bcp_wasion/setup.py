import sys
from cx_Freeze import setup, Executable

# Seu script principal (altere 'WS-BR.py' para o nome do seu script real)
main_script = 'WS-BR.py'

# Lista de outros scripts Python complementares
complementar_scripts = ['cSetup.py', 'cFuncionarios.py', 'cAlimentacao1.py']

# Lista de arquivos do banco de dados e arquivo CSV
files = ['modelo.db', 'funcionario.db', 'OE2-TRIFASICO-PIMA.csv']

# Configurações para o executável
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Se o seu script for uma GUI, use "Win32GUI"

executables = [Executable(main_script, base=base)]

# Opções de build
build_options = {
    "packages": ["os"],   # Coloque quaisquer pacotes externos que seu script utilize
    "excludes": [],   # Coloque quaisquer módulos que você deseja excluir
    "include_files": []
}

# Crie o executável
setup(
    name="WSBrasil",
    version="1.0",
    description="Registro de Máquinas",
    options={"build_exe": build_options},
    executables=executables
)
