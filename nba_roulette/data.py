"""Load validated player-team-season records for the game engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import PlayerTeamSeason


ROOT = Path(__file__).resolve().parent.parent


def load_records(
    seasons: Iterable[str] = ("1983-84", "1984-85", "1985-86", "1986-87", "1987-88", "1988-89", "1989-90", "1990-91", "1991-92", "1992-93", "1993-94", "1994-95", "1995-96", "1996-97", "1997-98", "1998-99", "1999-00", "2000-01", "2001-02", "2002-03", "2003-04", "2004-05", "2005-06", "2006-07", "2007-08", "2008-09", "2009-10", "2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"),
    data_dir: Path | None = None,
) -> tuple[PlayerTeamSeason, ...]:
    directory = data_dir or ROOT / "data" / "game"
    records: list[PlayerTeamSeason] = []
    for season in seasons:
        path = directory / f"players_{season.replace('-', '_')}.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing game dataset: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(PlayerTeamSeason.from_dict(row) for row in payload)
    if not records:
        raise ValueError("The roulette pool cannot be empty")
    keys = {(row.season, row.team, row.player_id) for row in records}
    if len(keys) != len(records):
        raise ValueError("Duplicate season/team/player records found")
    return tuple(records)


def load_goat_pools(data_dir: Path | None = None) -> dict[str, tuple[PlayerTeamSeason, ...]]:
    directory = data_dir or ROOT / "data" / "goat"
    pools = {}
    for name in ("award", "prehistoric"):
        rows = json.loads((directory / f"{name}_jackpot.json").read_text(encoding="utf-8"))
        if not rows or any(row.get("verification_status") != "official_verified" or row.get("pool") != name for row in rows):
            raise ValueError(f"GOAT pool {name} must contain only verified entries")
        records = tuple(PlayerTeamSeason.from_dict(row) for row in rows)
        if len({r.entry_id for r in records}) != len(records):
            raise ValueError(f"Duplicate GOAT entries in {name}")
        pools[name] = records
    return pools
