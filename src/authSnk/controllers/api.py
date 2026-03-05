from typing import Literal
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, model_validator
from src.authSnk.services.solucao import SolucaoService, AutenticacaoService
load_dotenv()

class SolucaoCadastroModel(BaseModel):
    descricao:str
    componente:str
    ambiente:Literal['prd','snd']
    clientId:str=None,
    clientSecret:str=None,
    xToken:str=None
    
    @model_validator(mode="after")
    def validarAmbiente(cls, model):
        if model.ambiente not in ['prd','snd']:
            raise ValueError("Ambiente deve ser 'prd' ou 'snd'")
        return model  

class SolucaoAtualizarModel(BaseModel):
    descricao:str=None
    componente:str=None
    ambiente:Literal['prd','snd']=None
    clientId:str=None,
    clientSecret:str=None,
    xToken:str=None
    
    @model_validator(mode="after")
    def validarAmbiente(cls, model):
        if model.ambiente not in ['prd','snd']:
            raise ValueError("Ambiente deve ser 'prd' ou 'snd'")
        return model      

class AutenticacaoLogarModel(BaseModel):
    solucaoId:int

router = APIRouter()

@router.post("/solucao/incluir", status_code=status.HTTP_201_CREATED)
async def incluir_solucao(payload:SolucaoCadastroModel) -> dict:
    res:dict={}    
    solucao = SolucaoService()
    try:
        res = await solucao.incluir(
            descricao=payload.descricao,
            componente=payload.componente,
            ambiente=payload.ambiente,
            clientId=payload.clientId,
            clientSecret=payload.clientSecret,
            xToken=payload.xToken
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        pass
    return res

@router.post("/solucao/atualizar/{id}", status_code=status.HTTP_202_ACCEPTED)
async def atualizar_solucao(payload:SolucaoCadastroModel, id:int):
    solucao = SolucaoService()
    try:
        await solucao.atualizar(
            id=id,
            descricao=payload.descricao,
            componente=payload.componente,
            ambiente=payload.ambiente,
            clientId=payload.clientId,
            clientSecret=payload.clientSecret,
            xToken=payload.xToken
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        pass

@router.delete("/solucao/{id}", status_code=status.HTTP_202_ACCEPTED)
async def excluir_solucao(id:int):
    solucao = SolucaoService()
    try:
        await solucao.excluir(id=id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        pass

@router.post("/autenticar/{solucaoId}", status_code=status.HTTP_200_OK)
async def autenticar(solucaoId:int) -> dict:
    autenticar = AutenticacaoService(solucaoId=solucaoId)
    sucesso, retorno = await autenticar.autenticar()
    if sucesso:
        return retorno
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=retorno.get('mensagem'))