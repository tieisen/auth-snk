from src.authSnk.database.database import AsyncSessionLocal
from sqlalchemy.future import select
from src.authSnk.database.models import Log
from src.authSnk.utils.database import validarDados, formatarRetorno

COLUNAS_CRIPTOGRAFADAS = []

class LogCrud:

    def __init__(self):
        pass

    async def criar(
        self,
        sucesso: bool,
        mensagem: str = "",
        solucaoId: int = None
    ) -> dict:
        log = {}

        async with AsyncSessionLocal() as session:
            log = Log(
                sucesso=sucesso,
                mensagem=mensagem,
                solucao_id=solucaoId
            )
            session.add(log)
            await session.commit()
            await session.refresh(log)
            
        return True

    async def buscar(
        self,
        solucaoId:int,
        sucesso:bool=None
    ) -> dict:

        async with AsyncSessionLocal() as session:
            if sucesso is None:
                result = await session.execute(
                    select(Log)
                    .where(Log.solucao_id == solucaoId)
                )
            else:
                result = await session.execute(
                    select(Log)
                    .where(Log.solucao_id == solucaoId,
                           Log.sucesso == sucesso)
                )
            
            logs = result.scalars().all()
            
        if not logs:
            raise ValueError(f"Nenhum log encontrado")
        
        return formatarRetorno(colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS,
                               retorno=logs)

    async def excluir(
        self,
        id:int
    ) -> bool:
        log = None
        
        async with AsyncSessionLocal() as session:                
            result = await session.execute(
                select(Log)
                .where(Log.id == id)
            )
            
            log = result.scalar_one_or_none()
            
            if not log:
                raise ValueError(f"Log não encontrado no banco de dados")
            else:
                await session.delete(log)
                await session.commit()
                log = True
                
        return log
