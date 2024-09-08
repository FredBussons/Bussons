import serial
from serial import SerialException
import logging
import atexit

# Configurar logging básico para capturar informações e erros
logging.basicConfig(level=logging.INFO)

class ArduinoHandler:
    def __init__(self, port='COM1', baudrate=9600, timeout=1):
        self.serial_conn = None  # Conexão serial com o Arduino
        self.port = port  # Porta de comunicação (ex: COM3)
        self.baudrate = baudrate  # Baud rate para comunicação serial
        self.timeout = timeout  # Tempo de espera (timeout) para comunicação serial
        
        # Registrar a desconexão automática quando o programa terminar
        atexit.register(self.disconnect)

    def connect(self):
        """Tenta conectar ao Arduino."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            logging.info(f"Conectado ao Arduino na porta {self.port} com baudrate {self.baudrate}")
            return True
        except SerialException as e:
            logging.error(f"Erro ao conectar ao Arduino: {e}")
            self.serial_conn = None
            return False

    def disconnect(self):
        """Desconecta o Arduino."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info("Arduino desconectado")

    def is_connected(self):
        """Verifica se o Arduino está conectado."""
        return self.serial_conn is not None and self.serial_conn.is_open

    def read_data(self):
        """Lê os dados enviados pelo Arduino."""
        if self.is_connected():
            try:
                data = self.serial_conn.readline().decode('utf-8').strip()  # Lê uma linha de dados
                logging.info(f"Dado recebido: {data}")
                return data
            except SerialException as e:
                logging.error(f"Erro ao ler dados do Arduino: {e}")
                self.disconnect()  # Se houver erro, desconectar
                # Tentar reconectar automaticamente após falha
                if self.reconnect():
                    logging.info("Reconexão bem-sucedida ao Arduino.")
                else:
                    logging.error("Falha ao reconectar ao Arduino.")
                return None
        else:
            logging.warning("Tentativa de leitura sem conexão ativa com o Arduino")
        return None

    def reconnect(self):
        """Tenta reconectar ao Arduino automaticamente."""
        self.disconnect()  # Desconecta qualquer conexão anterior
        return self.connect()  # Tenta reconectar

# Exemplo de uso (para teste local):
if __name__ == "__main__":
    arduino = ArduinoHandler(port='COM1', baudrate=9600)
    
    if arduino.connect():
        for _ in range(10):  # Ler dados 10 vezes como exemplo
            data = arduino.read_data()
            if data:
                print(f"Dados do Arduino: {data}")
            else:
                print("Nenhum dado recebido ou erro.")
            if not arduino.is_connected():  # Se desconectar, tentar reconectar
                if arduino.reconnect():
                    print("Reconectado ao Arduino.")
                else:
                    print("Falha ao reconectar.")
    else:
        print("Não foi possível conectar ao Arduino.")
    
    arduino.disconnect()
