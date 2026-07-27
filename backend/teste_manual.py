from app.core.history_analyzer import HistoryAnalyzer

with HistoryAnalyzer("https://github.com/pallets/flask") as analyzer:
    timeline = analyzer.build_timeline("src/flask/app.py", sample_step=20)
    print(f"Pontos na timeline: {len(timeline)}")
    for point in timeline:
        print(point)