from sqlalchemy import inspect
from src.authSnk.utils.criptografia import Criptografia
import datetime
from src.authSnk.utils.configLog import configLog
from dotenv import load_dotenv

load_dotenv()
logger = configLog(__name__)

def listarColunas(engine, nome_tabela: str) -> list[str]:
    """
    Retorna as colunas de uma tabela em formato de lista.
        :param engine: instância do SQLAlchemy Engine
        :param nome_tabela: nome da tabela no banco
    """
    inspector = inspect(engine)
    return [col["name"] for col in inspector.get_columns(nome_tabela)]


def listarColunasModel(modelo) -> list[str]:
    """
    Retorna as colunas a partir de um modelo do SQLAlchemy.
        :param modelo: classe do modelo (ex: Empresa)
    """
    return [col.name for col in modelo.__table__.columns]

def validarCriptografia(colunas_criptografadas:list[str], kwargs:dict) -> dict:
    """
    Criptografa os dados sensíveis.    
        :param colunas_criptografadas: lista de colunas a serem criptografadas
        :param kwargs: dados a serem criptografados
    """    
    cripto = Criptografia()
    try:
        for key, value in kwargs.items():
            if key in colunas_criptografadas and value:
                kwargs[key] = cripto.criptografar(value).decode()
    except Exception as e:
        erro = f"Erro ao criptografar dados da coluna {key}. {e}"
        logger.error(erro)
        return False    
    return kwargs

def removerCriptografia(colunas_criptografadas:list[str], dados:dict) -> dict:
    """
    Descriptografa os dados sensíveis.    
        :param colunas_criptografadas: lista de colunas a serem criptografadas
        :param dados: dados a serem descriptografados
    """        
    cripto = Criptografia()
    try:
        for key, value in dados.items():   
            if key in colunas_criptografadas and value:
                dados[key] = cripto.descriptografar(value)
    except Exception as e:
        erro = f"Erro ao descriptografar dados da coluna {key}. {e}"
        logger.error(erro)
        return False    
    return dados

def corrigirTimezone(dados:dict) -> dict:
    """
    Corrige o fuso horário dos campos de data (0 para -3)
        :param dados: dados a serem tratados
    """  
    br_tz = datetime.timezone(datetime.timedelta(hours=-3))
    for key, value in dados.items():
        if isinstance(value,datetime.datetime):
            dados[key] = value.astimezone(br_tz).replace(tzinfo=None)
    return dados

def formatarRetorno(colunas_criptografadas:list[str], retorno) -> dict:
    """
    Converte o retorno do SQLAlchemy em um dicionário, tratando os campos de data.
        :param colunas_criptografadas: lista de colunas de dados criptografados
        :param retorno: retorno do SQLAlchemy
    """        
    if not retorno:
        return False    
    
    if isinstance(retorno,list):
        retorno_formatado = []
        for r in retorno:
            r.__dict__.pop('_sa_instance_state', None)            
            dados = r.__dict__
            if colunas_criptografadas:
                dados = removerCriptografia(colunas_criptografadas,dados)            
            dados = corrigirTimezone(dados)
            dados.pop('token', None)
            dados.pop('xToken', None)            
            dados.pop('clientSecret', None)
            dados.pop('dhGeracaoToken', None)
            dados.pop('dhExpiracaoToken', None)
            retorno_formatado.append(dados)        
        return retorno_formatado
    
    retorno.__dict__.pop('_sa_instance_state', None)
    if colunas_criptografadas:
        dados = removerCriptografia(colunas_criptografadas,retorno.__dict__)
    dados = corrigirTimezone(retorno.__dict__)
    dados.pop('token', None)
    dados.pop('xToken', None)
    dados.pop('clientSecret', None)
    dados.pop('dhGeracaoToken', None)
    dados.pop('dhExpiracaoToken', None)
    return dados

def formatarRetornoAuth(colunas_criptografadas:list[str], retorno) -> dict:
    """
    Converte o retorno do SQLAlchemy em um dicionário, tratando os campos de data.
        :param colunas_criptografadas: lista de colunas de dados criptografados
        :param retorno: retorno do SQLAlchemy
    """        
    if not retorno:
        return False    
    
    if isinstance(retorno,list):
        retorno_formatado = []
        for r in retorno:
            r.__dict__.pop('_sa_instance_state', None)            
            dados = r.__dict__
            if colunas_criptografadas:
                dados = removerCriptografia(colunas_criptografadas,dados)            
            dados = corrigirTimezone(dados)
            retorno_formatado.append(dados)        
        return retorno_formatado
    
    retorno.__dict__.pop('_sa_instance_state', None)
    if colunas_criptografadas:
        dados = removerCriptografia(colunas_criptografadas,retorno.__dict__)
    dados = corrigirTimezone(retorno.__dict__)
    return dados
        
def validarColunasExistentes(modelo, kwargs:dict) -> dict:
    """
    Valida se as colunas informadas existem no banco de dados.
        :param modelo: classe do modelo (ex: Empresa)
        :param kwargs: dados no formato chave:valor
    """

    if not modelo:
        return False 
       
    colunas_do_banco = listarColunasModel(modelo)
    colunas_nao_encontradas = []
    # Verifica se existe coluna no banco para os dados informados
    for _ in kwargs.keys():
        if _ not in colunas_do_banco:
            colunas_nao_encontradas.append(_)    
    if colunas_nao_encontradas:
        erro = f"Coluna(s) [{', '.join(colunas_nao_encontradas)}] não encontrada(s) no banco de dados."
        logger.warning(erro)
        return False    
    return kwargs

def validarDados(modelo,kwargs:dict,colunas_criptografadas:list[str]=None) -> dict:
    """
    Valida as colunas dos dados e a criptografia.
        :param modelo: classe do modelo (ex: Empresa)
        :param kwargs: dados no formato chave:valor
        :param colunas_criptografadas: lista de colunas de dados criptografados
    """    
    if not validarColunasExistentes(modelo,kwargs):
        return False
    
    if colunas_criptografadas:
        if not validarCriptografia(colunas_criptografadas,kwargs):
            print("Erro ao criptografar dados.")
            return False
        
    return kwargs
