"""House of Minds: honest, testable data/game logic (no Streamlit dependency).

Human rounds use the collected real-participant dataset. Computer rounds
are independent fair-coin simulations; never recorded as human observations.
"""
from __future__ import annotations

import csv
import io
import random
import re
import secrets
from collections import Counter
from statistics import mean, median
from typing import Any


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


SEQUENCE_KEYS = [
    "coin_sequence", "coin_flip_sequence", "heads_tails", "heads/tails",
    "heads_tails_sequence", "flip_sequence", "sequence", "flips",
    "coin_flips", "ht_sequence", "coin_tosses", "coin_toss_sequence",
    "coinflip", "coin", "coin_flips_6", "coin_sequence_6", "sequence_6",
]
SMALL_KEYS = [
    "random_1_10", "random_1_to_10", "random_number_1_10", "random_number_1_to_10",
    "number_1_10", "number_1_to_10", "num_1_10", "random10", "rand10",
    "number10", "random_number_10", "random_number_small", "random_small",
    "random_number_1-10", "one_to_ten", "one_to_10", "num1",
    "number_1_10_first",
]
LARGE_KEYS = [
    "random_1_100", "random_1_to_100", "random_number_1_100", "random_number_1_to_100",
    "number_1_100", "number_1_to_100", "num_1_100", "random100", "rand100",
    "number100", "random_number_100", "random_number_large", "random_large",
    "random_number_1-100", "one_to_100", "num2",
]
COMBINED_KEYS = ["random_number", "random_numbers", "randomnumber", "randomnumbers",
                 "number_choices", "random_choices", "selected_numbers"]
ID_KEYS = ["participant_id", "participant", "person_number", "person", "person_id", "id"]


def _find_key(keys, candidates):
    lookup = {_norm(k): k for k in keys if k is not None}
    for candidate in candidates:
        if _norm(candidate) in lookup:
            return lookup[_norm(candidate)]
    return None


def clean_sequence(value: Any) -> str | None:
    if value is None:
        return None
    s = str(value).upper().strip().replace("HEADS", "H").replace("TAILS", "T")
    s = re.sub(r"[\s,;|/\-]", "", s)
    # The actual study includes both 6-flip and longer sequences. The game
    # compares equivalent six-flip prefixes; the full response stays in the CSV.
    return s[:6] if len(s) >= 6 and set(s) <= {"H", "T"} else None


def _int_range(value: Any, lo: int, hi: int) -> int | None:
    try:
        s = str(value).strip()
        if not s:
            return None
        f = float(s)
        if not f.is_integer() or not (lo <= int(f) <= hi):
            return None
        return int(f)
    except (TypeError, ValueError, OverflowError):
        return None


def parse_participants(csv_content: bytes | str) -> list[dict]:
    """Normalize common CSV/TSV column names, without fabricating missing data.

    Minimal required input: an actual six-flip coin sequence column. Random-number
    comparisons appear only if corresponding source fields are available.
    """
    text = (csv_content.decode("utf-8-sig") if isinstance(csv_content, bytes)
            else str(csv_content).lstrip("\ufeff"))
    if not text.strip():
        raise ValueError("The participant CSV is empty.")
    try:
        dialect = csv.Sniffer().sniff(text[:5000], delimiters=",;\t")
        delim = dialect.delimiter
    except csv.Error:
        delim = "\t" if "\t" in text.splitlines()[0] else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    if not reader.fieldnames:
        raise ValueError("No CSV headers found.")
    seq_key = _find_key(reader.fieldnames, SEQUENCE_KEYS)
    if not seq_key:
        raise ValueError("Coin sequence column not found. Accepted examples: "
                         "coin_sequence, heads_tails, Heads/Tails, flip_sequence.")
    small_key = _find_key(reader.fieldnames, SMALL_KEYS)
    large_key = _find_key(reader.fieldnames, LARGE_KEYS)
    combined_key = _find_key(reader.fieldnames, COMBINED_KEYS)
    id_key = _find_key(reader.fieldnames, ID_KEYS)
    type_key = _find_key(reader.fieldnames, ["data_type", "data_source", "source_type"])
    out = []
    for idx, row in enumerate(reader, 1):
        # Never silently promote synthetic/demo rows into the real-human class.
        if type_key:
            source = str(row.get(type_key) or "").strip().lower()
            if source not in ("", "real", "observed", "human"):
                continue
        original_seq = str(row.get(seq_key) or "").strip().upper()
        normalized_seq = re.sub(r"[\s,;|/\-]", "", original_seq)
        seq = clean_sequence(original_seq)
        if seq is None:
            continue  # no invented or repaired sequence
        small = _int_range(row.get(small_key), 1, 10) if small_key else None
        large = _int_range(row.get(large_key), 1, 100) if large_key else None
        if combined_key and (small is None or large is None):
            items = re.findall(r"\b\d{1,3}\b", str(row.get(combined_key) or ""))
            if len(items) >= 2:
                if small is None:
                    small = _int_range(items[0], 1, 10)
                if large is None:
                    large = _int_range(items[1], 1, 100)
        raw_id = str(row.get(id_key) or "").strip() if id_key else ""
        out.append({"id": raw_id or f"P{idx:03d}", "sequence": seq,
                    "original_sequence_length": len(normalized_seq),
                    "number_1_10": small, "number_1_100": large})
    if len(out) < 6:
        raise ValueError(f"Found only {len(out)} valid real participant sequences. "
                         "Need at least 6 real participants for a balanced game.")
    return out


def alternations(seq: str) -> int:
    return sum(a != b for a, b in zip(seq, seq[1:]))


def longest_run(seq: str) -> int:
    max_run, cur = 0, 0
    last = None
    for char in seq:
        cur = cur + 1 if char == last else 1
        max_run = max(max_run, cur)
        last = char
    return max_run


def sample_summary(rows: list[dict]) -> dict:
    seqs = [r["sequence"] for r in rows]
    short = [r["number_1_10"] for r in rows if r["number_1_10"] is not None]
    long = [r["number_1_100"] for r in rows if r["number_1_100"] is not None]
    return {
        "n": len(seqs), "heads_first": sum(s[0] == "H" for s in seqs),
        "mean_alternations": mean(alternations(s) for s in seqs),
        "median_alternations": median(alternations(s) for s in seqs),
        "mean_longest_run": mean(longest_run(s) for s in seqs),
        "small_counts": Counter(short), "small_n": len(short),
        "large_counts": Counter(long), "large_n": len(long),
        "longer_sequences": sum(r.get("original_sequence_length", 6) > 6 for r in rows),
    }


def predict_source(seq: str, head_rate: float) -> dict:
    """Simple, transparent first-flip classifier with 50/50 source prior."""
    p_first_human = head_rate if seq[0] == "H" else 1 - head_rate
    p_human = p_first_human / (p_first_human + .5)
    return {"label": "HUMAN" if p_human >= 0.5 else "COMPUTER",
            "p_human": p_human}


def create_game(rows: list[dict], num_rounds: int = 10) -> dict:
    """5 held-out human rounds + 5 genuine random rounds, shuffled.

    First-flip predictor estimates its rate from OTHER participants, so it
    cannot memorize any displayed participant's response. Repeated six-flip
    patterns may occur in both sources: identical sequences are not proof.
    """
    human_n = num_rounds // 2
    if len(rows) <= human_n:
        raise ValueError("Not enough real participants to hold out human rounds.")
    rng = random.Random(secrets.randbits(128))
    holdout_indices = set(rng.sample(range(len(rows)), human_n))
    train = [r for i, r in enumerate(rows) if i not in holdout_indices]
    heads = sum(r["sequence"][0] == "H" for r in train)
    head_rate = (heads + 1) / (len(train) + 2)  # Laplace smoothing
    rounds = []
    for i in holdout_indices:
        rounds.append({"sequence": rows[i]["sequence"], "source": "HUMAN"})
    for _ in range(num_rounds - human_n):
        seq = "".join("H" if rng.getrandbits(1) else "T" for _ in range(6))
        rounds.append({"sequence": seq, "source": "COMPUTER"})
    rng.shuffle(rounds)
    for item in rounds:
        item.update(predict_source(item["sequence"], head_rate))
        item["prediction"] = item.pop("label")
    return {"rounds": rounds, "train_n": len(train), "train_head_rate": head_rate}
