import tomllib
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.authSnk.controllers.solucao import router as routerSolucao
from src.authSnk.controllers.autenticacao import router as routerAutenticacao
from src.authSnk.utils.configLog import configLog
from authSnk.utils.paths import PROJECT_ROOT
from dotenv import load_dotenv

load_dotenv()
logger = configLog(__name__)
pyproject_file = PROJECT_ROOT / "pyproject.toml"

with open(pyproject_file, "rb") as f:
    config:dict = tomllib.load(f)

api_title:str = config['project'].get('name')
api_description:str = config['project'].get('description')
api_version:str = config['project'].get('version')

if not any([api_title,api_description,api_version]):
    raise ValueError("API config not found.")

app = FastAPI(title=api_title,
              description=api_description,
              version=api_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["*"],
)

app.include_router(routerSolucao, tags=["Soluções"])
app.include_router(routerAutenticacao, tags=["Autenticação"])

@app.get("/",include_in_schema=False)
def read_root():
    return {"message": f"{api_title}. Version {api_version}."}

print(f"===>>API Boot@{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"===>>API Boot@{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")