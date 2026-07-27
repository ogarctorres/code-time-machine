import subprocess
import tempfile
import shutil
import os

from radon.raw import analyze as radon_analyze
from radon.complexity import cc_visit
from dataclasses import dataclass
from typing import List


@dataclass
class CommitSnapshot:
    commit_hash: str
    date: str
    author: str


class HistoryAnalyzer:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.tmp_dir = None

    def __enter__(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="ctm_")
        self._clone()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _clone(self):
        subprocess.run(
            ["git", "clone", self.repo_url, self.tmp_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def list_commits_for_file(self, file_path: str) -> List[CommitSnapshot]:
        """Lista todos os commits que alteraram um arquivo específico, do mais antigo pro mais recente."""
        result = subprocess.run(
            [
                "git", "-C", self.tmp_dir,
                "log", "--follow",
                "--format=%H|%ai|%an",
                "--", file_path,
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        commits = []
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            commit_hash, date, author = line.split("|", 2)
            commits.append(CommitSnapshot(commit_hash=commit_hash, date=date, author=author))

        # o git log lista do mais recente pro mais antigo; invertemos pra ficar cronológico
        commits.reverse()
        return commits

    def get_file_content_at_commit(self, commit_hash: str, file_path: str) -> str:
        """Retorna o conteúdo de um arquivo exatamente como estava em um commit específico."""
        result = subprocess.run(
            ["git", "-C", self.tmp_dir, "show", f"{commit_hash}:{file_path}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        return result.stdout

    def build_timeline(self, file_path: str, sample_step: int = 10) -> list[dict]:
        """
        Monta a linha do tempo de métricas de um arquivo, amostrando
        1 a cada `sample_step` commits para não processar tudo.
        """
        all_commits = self.list_commits_for_file(file_path)
        sampled_commits = all_commits[::sample_step]

        # garante que o commit mais recente sempre entra na amostra,
        # mesmo que o sample_step "pule" ele
        if all_commits and sampled_commits[-1] != all_commits[-1]:
            sampled_commits.append(all_commits[-1])

        timeline = []
        for commit in sampled_commits:
            try:
                code = self.get_file_content_at_commit(commit.commit_hash, file_path)
                raw_metrics = radon_analyze(code)
                complexities = cc_visit(code)

                avg_complexity = (
                    sum(c.complexity for c in complexities) / len(complexities)
                    if complexities else 0
                )

                timeline.append({
                    "commit_hash": commit.commit_hash,
                    "date": commit.date,
                    "author": commit.author,
                    "lines_of_code": raw_metrics.loc,
                    "num_functions": len(complexities),
                    "avg_complexity": round(avg_complexity, 2),
                })
            except Exception:
                # se o arquivo não existia nesse commit ainda, ou não é Python válido, pula
                continue

        return timeline