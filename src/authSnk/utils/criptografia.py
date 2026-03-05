import os
from cryptography.fernet import Fernet
from src.authSnk.utils.configLog import configLog
from dotenv import load_dotenv

load_dotenv()
logger = configLog(__name__)

class Criptografia:
    def __init__(self):
        """
        Inicializa a classe com uma chave Fernet.
        """
        self.path = os.getenv('PATH_FERNET_KEY')
        chave = self.ler_key()
        if not chave:
            chave = Fernet.generate_key()
            self.chave = chave
            self.salvar_key()
        self.chave = chave
        self.fernet = Fernet(self.chave)

    def buscarChave(self) -> bytes:
        """
        Retorna a chave usada na criptografia.
        """
        return self.chave

    def criptografar(self, mensagem: str) -> bytes:
        """
        Criptografa uma string e retorna em bytes.
            :param mensagem: texto a ser criptografado
        """
        if isinstance(mensagem,bytes):
            return self.fernet.encrypt(mensagem)
        else:
            return self.fernet.encrypt(mensagem.encode())

    def descriptografar(self, mensagem: bytes) -> str:
        """
        Descriptografa a mensagem e retorna como string.
            :param mensagem: texto a ser descriptografado
        """
        return self.fernet.decrypt(mensagem).decode()
    
    def salvarChave(self) -> bool:
        """
        Salva a chave em um arquivo.
        """
        try:
            with open(self.path, "wb") as arquivo:
                arquivo.write(self.chave)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar a chave: {e}")            
            return False
        
    def lerChave(self) -> bytes:
        """
        Lê a chave de um arquivo.
        """
        try:
            with open(self.path, "rb") as arquivo:
                chave = arquivo.read()
            return chave
        except Exception as e:            
            logger.error(f"Erro ao ler a chave: {e}")
            return None