import logging, pytest, shutil, os
from pathlib import Path
from purrgress.plog.config import CFG
from purrgress.utils.path import resolve_pathish

@pytest.fixture
def tmp_data_dir(tmp_path, monkeypatch):
    test_root = tmp_path / "purrgress" / "data"
    test_root.mkdir(parents=True)

    monkeypatch.setattr("purrgress.plog.core.DATA_ROOT", test_root, raising=False)

    from purrgress.plog import core
    monkeypatch.setattr(
        core, "DRAFT_FILE", test_root / ".draft.yaml", raising=False
    )
    return test_root

@pytest.fixture
def cfg(monkeypatch):
    
    CFG_CACHE = CFG()
    yield CFG_CACHE

@pytest.fixture(autouse=True)
def _mute_logs():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
