from src.authSnk.database.database import AsyncSessionLocal
from sqlalchemy.future import select
from src.authSnk.database.models import Solucao
from src.authSnk.utils.database import validarDados, formatarRetorno, formatarRetornoAuth

COLUNAS_CRIPTOGRAFADAS = [
        'clientSecret',
        'xToken',
        'token'
    ]

class SolucaoCrud:

    def __init__(self):
        pass

    async def criar(
        self,
        descricao: str,
        componente: str,
        ambiente: str,
        **kwargs
    ) -> dict:
        solucao = {}

        if kwargs:
            kwargs = validarDados(modelo=Solucao,
                                  kwargs=kwargs,
                                  colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS)
            if not kwargs:
                return solucao
        
        async with AsyncSessionLocal() as session:                
            result = await session.execute(
                select(Solucao)
                .where(Solucao.descricao == descricao,
                       Solucao.componente == componente,
                       Solucao.ambiente == ambiente)
            )
            
            solucao = result.scalar_one_or_none()
            if solucao:
                raise ValueError(f"Já existe uma solução com a descrição {descricao}, componente {componente} e ambiente {ambiente} no banco de dados. ID: {solucao.id}")
            else:
                solucao = Solucao(
                    descricao=descricao,
                    componente=componente,
                    ambiente=ambiente,
                    **kwargs
                )
                session.add(solucao)
                await session.commit()
                await session.refresh(solucao)
            
        return formatarRetorno(colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS,
                               retorno=solucao)

    async def buscar(
        self,
        id:int=None,
        descricao:str=None,
        componente:str=None,
        ambiente:str=None
    ) -> dict:

        if not id and not any([descricao,componente,ambiente]):
            raise ValueError("Nenhum parâmetro informado para pesquisa.")
        
        async with AsyncSessionLocal() as session:

            filtros = []

            if id:
                filtros.append(Solucao.id == id)
            if descricao:
                filtros.append(Solucao.descricao == descricao)
            if componente:
                filtros.append(Solucao.componente == componente)
            if ambiente:
                filtros.append(Solucao.ambiente == ambiente)

            query = select(Solucao)

            if filtros:
                query = query.where(*filtros)

            result = await session.execute(query)                
                        
            solucao = result.scalars().all()
            
        if not solucao and id:
            raise ValueError(f"Solução não encontrada no banco de dados.\nID: {id}")
        if not solucao and not id:
            raise ValueError(f"Solução não encontrada no banco de dados.\nDescrição: {descricao} | Componente: {componente} | Ambiente: {ambiente}")
        
        return formatarRetorno(colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS,
                               retorno=solucao)

    async def buscarAutenticacao(
        self,
        id:int
    ) -> dict:
        async with AsyncSessionLocal() as session:
            query = select(Solucao)
            query = query.where(Solucao.id == id)
            result = await session.execute(query)                        
            solucao = result.scalars().all()
            
        if not solucao:
            raise ValueError(f"Solução não encontrada no banco de dados.\nID: {id}")
        
        return formatarRetornoAuth(colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS,
                                   retorno=solucao)
    
    async def atualizar(
        self,
        id:int,
        **kwargs
    ) -> bool:
        solucao = None

        if kwargs:
            kwargs = validarDados(modelo=Solucao,
                                  kwargs=kwargs,
                                  colunas_criptografadas=COLUNAS_CRIPTOGRAFADAS)
            if not kwargs:
                return solucao
                    
        async with AsyncSessionLocal() as session:                
            result = await session.execute(
                select(Solucao)
                .where(Solucao.id == id)
            )   
                     
            solucao = result.scalar_one_or_none()            
            if not solucao:
                raise ValueError(f"Solução {id} não encontrada no banco de dados")
            else:
                for key, value in kwargs.items():
                    if value:
                        setattr(solucao, key, value)
                await session.commit()
                solucao = True 
                           
        return solucao

    async def excluir(
        self,
        id:int
    ) -> bool:
        solucao = None
        
        async with AsyncSessionLocal() as session:                
            result = await session.execute(
                select(Solucao)
                .where(Solucao.id == id)
            )
            
            solucao = result.scalar_one_or_none()
            
            if not solucao:
                raise ValueError(f"Solução {id} não encontrada no banco de dados")
            else:
                await session.delete(solucao)
                await session.commit()
                solucao = True
                
        return solucao
