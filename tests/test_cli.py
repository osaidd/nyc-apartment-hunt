import io
import json
import pathlib
import shutil

import nyc_hunt.cli as cli
from nyc_hunt.models import Listing

REPO = pathlib.Path(cli.__file__).parents[2]


def _setup(tmp_path):
    shutil.copy(pathlib.Path(cli.__file__).parent / "config.example.toml", tmp_path / "config.toml")
    return str(tmp_path / "config.toml")


def test_example_configs_in_sync():
    assert (REPO / "config.example.toml").read_text() == \
        (pathlib.Path(cli.__file__).parent / "config.example.toml").read_text()


def test_run_with_stubbed_sources(tmp_path, monkeypatch, capsys):
    cfg = _setup(tmp_path)
    fake = [Listing(url="https://x/1", source="craigslist", search_type="studio_1br",
                    price=3000, neighborhood="Chelsea", no_fee=True)]
    monkeypatch.setattr(cli, "SOURCES", {"craigslist": lambda c: fake, "renthop": lambda c: 1 / 0})
    rc = cli.main(["run", "--config", cfg, "--no-email"])
    out, err = capsys.readouterr()
    assert rc == 0 and "found=1 new=1 dup=0 high=1" in out
    assert "renthop" in err  # blocked source reported
    assert (tmp_path / "reports" / "latest.html").exists()


def test_run_all_sources_fail(tmp_path, monkeypatch):
    cfg = _setup(tmp_path)
    monkeypatch.setattr(cli, "SOURCES", {"craigslist": lambda c: 1 / 0})
    assert cli.main(["run", "--config", cfg, "--no-email"]) == 1


def test_add_json_stdin(tmp_path, monkeypatch, capsys):
    cfg = _setup(tmp_path)
    rows = [{"url": "https://se.com/1", "source": "streeteasy", "search_type": "2br_2ba",
             "price": 4800, "beds": 2, "baths": 2, "neighborhood": "Chelsea", "no_fee": True},
            {"bad": "row"}]
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(rows)))
    rc = cli.main(["add", "--json", "-", "--config", cfg])
    out = capsys.readouterr().out
    assert rc == 0 and "found=2 new=1" in out and "skipped_invalid=1" in out


def test_init_and_report(tmp_path, capsys):
    cfg = str(tmp_path / "config.toml")
    assert cli.main(["init", "--config", cfg]) == 0
    assert cli.main(["init", "--config", cfg]) == 1  # refuses overwrite
    assert cli.main(["report", "--config", cfg]) == 0
    assert "found=0" in capsys.readouterr().out
