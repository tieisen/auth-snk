import os, requests
from datetime import datetime, timedelta
from src.authSnk.database.crud.solucao import SolucaoCrud
from src.authSnk.database.crud.log import LogCrud
from src.authSnk.utils.configLog import configLog
from dotenv import load_dotenv

load_dotenv()
logger = configLog(__name__)

class AutenticacaoService:

    def __init__(self, solucaoId:int, xToken:str): 
        self.solucao_id = solucaoId
        self.xToken = xToken
        self.solucao_crud = SolucaoCrud()
        self.log_crud = LogCrud()
        self.dados_solucao:dict = {}

    async def registrarLog(self,sucesso:bool,mensagem:str) -> bool:
        return await self.log_crud.criar(
            solucaoId=self.solucao_id,
            sucesso=sucesso,
            mensagem=mensagem
        )

    async def logar(self) -> dict:
        
        if not self.dados_solucao:
            self.dados_solucao = await self.buscarToken()
            
        url:str = os.getenv("URL_LOGIN_PRD") if self.dados_solucao.get('ambiente') == 'prd' else os.getenv("URL_LOGIN_SND")        

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
            url=url,
            headers=header,
            data=body
        )
        
        if res.ok:
            auth = res.json()
        else:
            mensagem_erro = f"Erro {res.status_code} ao autenticar: {res.text}"
            logger.error(mensagem_erro)
            logger.info("url: %s",url)
            logger.info("header: %s",header)
            logger.info("body: %s",body)
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
        return (await self.solucao_crud.buscarAutenticacao(id=self.solucao_id))[0]
        
    async def autenticar(self) -> tuple[bool, dict]:
        """
        Realiza a autenticação baseada nos dados da solução. 
        Busca o token no banco; se expirado ou inexistente, realiza novo login.
        """
        
        token_string:str = ""
        token_atual:str = ""
        dh_expiracao:datetime = None
        dh_geracao:datetime = None
        sucesso:bool = False
        mensagem:str = ""
        retorno:dict = {"token": "", "dhExpiracaoToken": "", "mensagem": ""}
        
        try:            
            if not self.dados_solucao:
                self.dados_solucao = await self.buscarToken()

            if self.dados_solucao.get('xToken') != self.xToken:
                raise PermissionError('xToken inválido')
            
            token_atual = self.dados_solucao.get('token')
            dh_expiracao = self.dados_solucao.get('dhExpiracaoToken')

            # Verifica se o token ainda é válido (com margem de 1 minuto)
            if token_atual and dh_expiracao:
                if dh_expiracao > (datetime.now(tz=dh_expiracao.tzinfo) + timedelta(minutes=1)):
                    sucesso = True
                    mensagem = "Autenticado com sucesso"
                    token_string = token_atual

            if not sucesso:
                # Se não houver token ou estiver expirado, realiza novo login
                novo_token_data = await self.logar()
                
                token_string = novo_token_data.get('access_token')
                expires_in = novo_token_data.get('expires_in')            
                if not all([token_string,expires_in]):
                    raise ValueError("Token ou tempo de expiração não encontrado na resposta do login")
                
                dh_geracao = datetime.now()
                dh_expiracao = await self.calcularExpiracao(segundos=expires_in)
                
                # Salva o token no banco
                await self.salvarToken(
                    novoToken=token_string,
                    dhGeracaoToken=dh_geracao,
                    dhExpiracaoToken=dh_expiracao
                )
                
                mensagem = "Autenticado com sucesso"
                sucesso = True
            
        except Exception as e:
            mensagem = f"Erro ao autenticar: {e}"            
            logger.error(mensagem)
                        
        finally:
            await self.registrarLog(sucesso=sucesso, mensagem=mensagem)
            retorno = {
                "solucaoId": self.solucao_id,
                "token": token_string,
                "dhExpiracaoToken": dh_expiracao,
                "mensagem": mensagem
            }
        
        return (sucesso, retorno)
    