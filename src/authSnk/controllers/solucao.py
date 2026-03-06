from typing import Literal
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, model_validator
from src.authSnk.services.solucao import SolucaoService
load_dotenv()

class SolucaoCadastroModel(BaseModel):
    descricao:str
    componente:str
    ambiente:Literal['prd','snd']
    clientId:str
    clientSecret:str
    xToken:str | None = None
    
    @model_validator(mode="after")
    def validarAmbiente(cls, model):
        if model.ambiente not in ['prd','snd']:
            raise ValueError("Ambiente deve ser 'prd' ou 'snd'")
        return model

class SolucaoAtualizarModel(BaseModel):
    descricao:str | None = None
    componente:str | None = None
    ambiente:Literal['prd','snd'] | None = None
    clientId:str | None = None
    clientSecret:str | None = None
    xToken:str | None = None
    
    @model_validator(mode="after")
    def validarAmbiente(cls, model):
        if model.ambiente and model.ambiente not in ['prd','snd']:
            raise ValueError("Ambiente deve ser 'prd' ou 'snd'")
        return model 

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

@router.get("/solucao/{id}", status_code=status.HTTP_200_OK)
async def buscar_solucao_id(id:int) -> dict:
    res:dict={}    
    solucao = SolucaoService()
    try:
        res = (await solucao.buscar(id=id))[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        pass
    return res

@router.get("/solucao", status_code=status.HTTP_200_OK)
async def buscar_solucao(descricao: str | None = None, componente: str | None = None, ambiente: str | None = None) -> list[dict]:
    res:dict={}    
    solucao = SolucaoService()
    
    try:
        res = await solucao.buscar(
            descricao=descricao,
            componente=componente,
            ambiente=ambiente
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        pass
    return res

@router.put("/solucao/{id}", status_code=status.HTTP_202_ACCEPTED)
async def atualizar_solucao(payload:SolucaoAtualizarModel, id:int):
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