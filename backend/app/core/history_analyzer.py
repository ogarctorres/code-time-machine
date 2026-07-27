import subprocess
import tempfile
import shutil
import os
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