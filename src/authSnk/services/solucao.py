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

    async def registrarLog(self,sucesso:bool,mensagem:str,solucaoId:int=None) -> bool:
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
        clientId:str,
        clientSecret:str,
        xToken:str
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
                sucesso=ack,
                mensagem=f"ID {id} excluído com sucesso"
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
