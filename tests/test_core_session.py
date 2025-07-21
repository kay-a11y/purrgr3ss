from purrgress.plog import core

def test_start_stop_roundtrip(tmp_data_dir, monkeypatch):
    draft = core.start_session("unit-task", [], [], tz="UTC")
    assert draft["task"] == "unit-task"
    assert core.DRAFT_FILE.exists()

    stored = core.stop_session(tz="UTC")
    assert not core.DRAFT_FILE.exists()
    year, month = draft["date"].split("-")[:2]
    yaml_path = tmp_data_dir / f"{year}/{month}.yaml"
    assert yaml_path.exists()