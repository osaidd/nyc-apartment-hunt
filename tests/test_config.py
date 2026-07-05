import pathlib
import shutil

import pytest

from nyc_hunt.config import ConfigError, load


def test_load_example(tmp_path):
    p = tmp_path / "config.toml"
    shutil.copy(pathlib.Path(__file__).parent.parent / "config.example.toml", p)
    cfg = load(p)
    assert [s.name for s in cfg.searches] == ["studio_1br", "2br_2ba"]
    assert cfg.searches[0].max_price == 3600 and cfg.searches[1].baths_min == 2
    assert "Chelsea" in cfg.tier1 and cfg.email.enabled is False
    assert cfg.search_by_name("2br_2ba").max_price == 5000


def test_missing_search_raises(tmp_path):
    p = tmp_path / "c.toml"
    p.write_text("[hunt]\nmove_in='2026-09-01'\n")
    with pytest.raises(ConfigError):
        load(p)
