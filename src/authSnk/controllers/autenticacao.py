from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
from src.authSnk.services.autenticacao import AutenticacaoService

class AutenticacaoLogarModel(BaseModel):
    solucaoId:int
    
class AutenticacaoResponse(BaseModel):
    solucaoId: str
    token: str
    dhExpiracaoToken: str
    mensagem: str

router = APIRouter()
header_scheme = APIKeyHeader(name="xToken")

@router.post("/autenticar/{solucaoId}", status_code=status.HTTP_200_OK, response_model=AutenticacaoResponse)
async def autenticar(solucaoId:int, xToken: str = Depends(header_scheme)) -> dict:
    autenticacao_service = AutenticacaoService(solucaoId, xToken)
    sucesso, retorno = await autenticacao_service.autenticar()
    if sucesso:
        return retorno
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=retorno.get('mensagem'))