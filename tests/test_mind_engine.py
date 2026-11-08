from collections import Counter
from pathlib import Path

import pytest

from mind_engine import (
    alternations, clean_sequence, create_game, longest_run,
    parse_participants, predict_source, sample_summary,
)

REAL_CSV = Path(__file__).resolve().parents[1] / "participants.csv"


def participants():
    return parse_participants(REAL_CSV.read_bytes())


def test_original_dataset_all_36_people_loaded():
    rows = participants()
    assert len(rows) == 36
    assert len({r["id"] for r in rows}) == 36
    assert sum(r["sequence"].startswith("H") for r in rows) == 28
    assert all(len(r["sequence"]) == 6 for r in rows)


def test_longer_sequences_are_first_six_only():
    rows = participants()
    assert sum(r["original_sequence_length"] > 6 for r in rows) == 17
    assert rows[0]["sequence"] == "TTHHTH"
    assert rows[0]["original_sequence_length"] == 15


def test_real_number_fields_load():
    rows = participants()
    assert rows[0]["number_1_10"] == 7
    assert rows[0]["number_1_100"] == 77
    summary = sample_summary(rows)
    assert summary["small_n"] == 36
    assert summary["large_n"] == 36
    assert summary["longer_sequences"] == 17


def test_invalid_csv_rejected():
    with pytest.raises(ValueError):
        parse_participants("random_number\n7\n")
    with pytest.raises(ValueError):
        parse_participants("heads_tails\nHHHTTT\n")


def test_synthetic_rows_not_treated_as_human():
    text = "participant_id,heads_tails,data_type\n"
    text += "0,HHHTTT,synthetic_demo\n"
    text += "".join(f"{i},HHHTTT,real\n" for i in range(1, 8))
    people = parse_participants(text)
    assert len(people) == 7
    assert "0" not in [p["id"] for p in people]


def test_sequence_stats():
    assert clean_sequence("hththt") == "HTHTHT"
    assert clean_sequence("hthththththt") == "HTHTHT"
    assert clean_sequence("HHHXTH") is None
    assert alternations("HTHTHT") == 5
    assert alternations("HHHHHH") == 0
    assert longest_run("TTHHHH") == 4


def test_balanced_game():
    game = create_game(participants())
    assert len(game["rounds"]) == 10
    assert Counter(x["source"] for x in game["rounds"]) == {"HUMAN": 5, "COMPUTER": 5}
    assert game["train_n"] == 31
    assert all(len(x["sequence"]) == 6 for x in game["rounds"])
    assert all(x["prediction"] in ("HUMAN", "COMPUTER") for x in game["rounds"])


def test_first_flip_baseline():
    assert predict_source("HHHTTT", 0.8)["label"] == "HUMAN"
    assert predict_source("THHTTT", 0.8)["label"] == "COMPUTER"
