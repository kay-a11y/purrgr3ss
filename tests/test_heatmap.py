from purrgress.plog.reports import make_heatmap
from pathlib import Path

def test_make_heatmap(tmp_data_dir, monkeypatch):
    month = tmp_data_dir / "2025" / "07.yaml"
    month.parent.mkdir(parents=True, exist_ok=True)
    month.write_text("'2025-07-01': {sessions: []}")
    out = make_heatmap(2025, 7, theme="viridis")
    assert Path(out).exists()
