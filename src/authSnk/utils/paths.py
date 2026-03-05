from pathlib import Path

def procuraRaizProjeto() -> Path:
    """
    Procura a raiz do projeto baseada na presença do pyproject.toml
    """
    current = Path(__file__).resolve()

    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Raiz do projeto não encontrada")


PROJECT_ROOT = procuraRaizProjeto()

SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"