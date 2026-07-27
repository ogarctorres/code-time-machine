from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.history_analyzer import HistoryAnalyzer

router = APIRouter()


class TimelineRequest(BaseModel):
    repo_url: str = Field(..., description="URL pública do repositório, ex: https://github.com/org/repo")
    file_path: str = Field(..., description="Caminho do arquivo dentro do repositório, ex: src/app.py")
    sample_step: int = Field(10, ge=1, le=100, description="Amostra 1 a cada N commits")


@router.post("/timeline")
def get_timeline(payload: TimelineRequest):
    if "github.com" not in payload.repo_url:
        raise HTTPException(status_code=400, detail="Por enquanto só suportamos repositórios do GitHub.")

    if not payload.file_path.endswith(".py"):
        raise HTTPException(status_code=400, detail="Por enquanto só suportamos arquivos Python (.py).")

    try:
        with HistoryAnalyzer(payload.repo_url) as analyzer:
            timeline = analyzer.build_timeline(payload.file_path, sample_step=payload.sample_step)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Falha ao analisar arquivo: {exc}") from exc

    if not timeline:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para esse arquivo. Confira o caminho.")

    return {
        "repo_url": payload.repo_url,
        "file_path": payload.file_path,
        "timeline": timeline,
    }


@router.get("/health")
def health():
    return {"status": "ok"}