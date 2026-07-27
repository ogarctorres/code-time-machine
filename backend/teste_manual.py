from app.core.history_analyzer import HistoryAnalyzer

with HistoryAnalyzer("https://github.com/pallets/flask") as analyzer:
    commits = analyzer.list_commits_for_file("src/flask/app.py")
    print(f"Total de commits: {len(commits)}")
    print("Primeiro commit:", commits[0])
    print("Último commit:", commits[-1])