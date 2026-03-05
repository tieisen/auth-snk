import os, requests
from datetime import datetime, timedelta
from src.authSnk.database.crud.solucao import SolucaoCrud
from src.authSnk.database.crud.log import LogCrud
from src.authSnk.utils.configLog import configLog
from dotenv import load_dotenv

load_dotenv()
logger = configLog(__name__)

class SolucaoService:
    
    def __init__(self): 
        self.solucao_crud = SolucaoCrud()
        self.log_crud = LogCrud()

    async def registrarLog(self,solucaoId:int,sucesso:bool,mensagem:str) -> bool:
        return await self.log_crud.criar(
            solucaoId=solucaoId,
            sucesso=sucesso,
            mensagem=mensagem
        )
        
    async def incluir(
        self,
        descricao:str,
        componente:str,
        ambiente:str,
        clientId:str=None,
        clientSecret:str=None,
        xToken:str=None
    ) -> dict:
        
        dados_solucao:dict = {}
        
        try:
            dados_solucao = await self.solucao_crud.criar(
                descricao = descricao,
                componente = componente,
                ambiente = ambiente,
                clientId = clientId,
                clientSecret = clientSecret,
                xToken = xToken
            )
            await self.registrarLog(
                solucaoId=dados_solucao.get('id'),
                sucesso=True,
                mensagem="Incluído com sucesso"
            )            
            return dados_solucao
        except Exception as e:
            msg_erro:str = f"Erro ao incluir solução {descricao}/{componente}/{ambiente} no banco: {e}"
            logger.error(msg_erro)
            await self.registrarLog(
                sucesso=False,
                mensagem=msg_erro
            )            
            raise Exception(msg_erro)
        
    async def buscar(
        self,
        id: int = None,
        descricao: str = None,
        componente: str = None,
        ambiente: str = None
    ) -> dict:
        dados_solucao:dict = {}        
        try:
            dados_solucao = await self.solucao_crud.buscar(
                id=id,
                descricao=descricao,
                componente=componente,
                ambiente=ambiente
            )            
            return dados_solucao
        except Exception as e:
            msg_erro:str = f"Erro ao buscar dados no banco: {e}"
            logger.error(msg_erro)
            await self.registrarLog(
                solucaoId=dados_solucao.get('id'),
                sucesso=False,
                mensagem=msg_erro
            )                        
            raise Exception(msg_erro)
        
    async def atualizar(
        self,
        id: int = None,
        descricao: str = None,
        componente: str = None,
        ambiente: str = None,
        **kwargs
    ) -> dict:
        dados_solucao:dict = {}
        ack:bool = False
        try:
            if not id and all([descricao,componente,ambiente]):
                dados_solucao = await self.solucao_crud.buscar(descricao=descricao, componente=componente, ambiente=ambiente)
                id = dados_solucao.get('id')
                
            ack:bool = await self.solucao_crud.atualizar(
                id=id,
                **kwargs
            )
            
            await self.registrarLog(
                solucaoId=id,
                sucesso=ack,
                mensagem="Atualizado com sucesso"
            )
            
            return ack
            
        except Exception as e:
            msg_erro:str = f"Erro ao atualizar solução no banco: {e}"
            logger.error(msg_erro)
            await self.registrarLog(
                solucaoId=id,
                sucesso=ack,
                mensagem=msg_erro
            )            
            raise Exception(msg_erro)
        
    async def excluir(
        self,
        id: int
    ) -> dict:
        ack:bool = False
        try:
            ack = await self.solucao_crud.excluir(id=id)
            await self.registrarLog(
                solucaoId=id,
                sucesso=ack,
                mensagem="Excluído com sucesso"
            )            
            return ack        
        except Exception as e:
            msg_erro:str = f"Erro ao excluir solução do banco: {e}"
            logger.error(msg_erro)
            await self.registrarLog(
                solucaoId=id,
                sucesso=ack,
                mensagem=msg_erro
            )              
            raise Exception(msg_erro)

class AutenticacaoService:

    def __init__(self, solucaoId:int): 
        self.solucao_id = solucaoId       
        self.solucao_crud = SolucaoCrud()
        self.log_crud = LogCrud()
        self.dados_solucao:dict = self.solucao_crud.buscar(id=solucaoId)
        self.url_login = os.getenv("URL_LOGIN")

    async def registrarLog(self,sucesso:bool,mensagem:str) -> bool:
        return await self.log_crud.criar(
            solucaoId=self.solucao_id,
            sucesso=sucesso,
            mensagem=mensagem
        )

    async def logar(self) -> dict:

        auth:dict={}
        
        header = {
            'X-Token':self.dados_solucao.get('xToken'),
            'accept':'application/x-www-form-urlencoded',
            'content-type':'application/x-www-form-urlencoded'
        }

        body = {
            'grant_type':'client_credentials',
            'client_id':self.dados_solucao.get('clientId'),
            'client_secret':self.dados_solucao.get('clientSecret'),
        }

        res = requests.post(
            url=self.url_login,
            headers=header,
            data=body)
        
        if res.ok:
            auth = res.json()
        else:
            mensagem_erro = f"Erro {res.status_code} ao autenticar: {res.text}"
            logger.error(mensagem_erro)
            raise Exception(mensagem_erro)

        return auth
    
    async def calcularExpiracao(self, segundos: int) -> datetime:
        try:
            return datetime.now() + timedelta(seconds=segundos)
        except Exception as e:
            raise Exception(f"Erro ao calcular expiração do token: {e}")
        
    async def salvarToken(self, novoToken:str, dhGeracaoToken:datetime, dhExpiracaoToken:datetime) -> bool:

        status:bool = False
        status = await self.solucao_crud.atualizar(
            id=self.solucao_id,
            token=novoToken,
            dhGeracaoToken=dhGeracaoToken,
            dhExpiracaoToken=dhExpiracaoToken
        )
        return status
        
    async def buscarToken(self) -> dict:        
        return await self.solucao_crud.buscar(id=self.solucao_id)
        
    async def autenticar(self) -> tuple[bool, dict]:
        """
        Realiza a autenticação baseada nos dados da solução. 
        Busca o token no banco; se expirado ou inexistente, realiza novo login.
        """
        
        token_string:str = ""
        sucesso:bool = True
        mensagem:str = ""
        retorno:dict = {"token": "", "dhExpiracaoToken": "", "mensagem": ""}
        
        try:
            # Busca os dados da solução (já descriptografados pelo service)
            solucao_dados:dict = await self.buscarToken()
            
            token_atual = solucao_dados.get('token')
            dh_expiracao = solucao_dados.get('dhExpiracaoToken')

            # Verifica se o token ainda é válido (com margem de 1 minuto)
            if token_atual and dh_expiracao:
                if dh_expiracao > (datetime.now() + timedelta(minutes=1)):
                    return token_atual

            # Se não houver token ou estiver expirado, realiza novo login
            novo_token_data = await self.logar()
            
            token_string = novo_token_data.get('access_token')
            expires_in = novo_token_data.get('expires_in')            
            if not all([token_string,expires_in]):
                raise ValueError("Token ou tempo de expiração não encontrado na resposta do login")
            
            dh_geracao = datetime.now()
            dh_expiracao = self.calcularExpiracao(segundos=expires_in)
            
            # Salva o token no banco
            await self.salvarToken(
                novoToken=token_string,
                dhGeracaoToken=dh_geracao,
                dhExpiracaoToken=dh_expiracao
            )
            
            mensagem = "Autenticado com sucesso"
            
        except Exception as e:
            sucesso = False
            mensagem = f"Erro ao autenticar: {e}"            
            logger.error(mensagem)
            print(mensagem)
                        
        finally:
            await self.registrarLog(sucesso=sucesso, mensagem=mensagem)
            retorno = {
                "token": token_string,
                "dhExpiracaoToken": dh_expiracao,
                "mensagem": mensagem
            }
        
        return (sucesso, retorno)
    