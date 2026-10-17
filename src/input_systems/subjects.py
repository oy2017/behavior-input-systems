"""Matched subject tables.

Track A: subjects behind BehaviorBench's Masked-Resp task, matched by content
(their 49 known item answers) to the public openpsychometrics BIG5 file, which
gives demographics + all 50 answers + IPIP scores for the same person.
The BehaviorBench index file does NOT index raw rows, so do not use it here.

Track B: the Across-Ctx records, keyed by metadata.user_id; history games
(instruction + choice) are parsed from the record's own prompt.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

DIMS = "ENACO"
COLS = [f"{d}{i}" for d in DIMS for i in range(1, 11)]
_REVERSED = {"E": {2, 4, 6, 8, 10}, "N": {2, 4}, "A": {1, 3, 5, 7}, "C": {2, 4, 6, 8}, "O": {2, 4, 6}}
DIM_NAME = {"E": "Extraversion", "N": "Neuroticism", "A": "Agreeableness",
            "C": "Conscientiousness", "O": "Openness"}
GENDER = {"1": "male", "2": "female", "3": "other"}
HAND = {"1": "Right-handed", "2": "Left-handed", "3": "Ambidextrous"}
RACE = {"1": "Mixed Race", "2": "Arctic (Siberian, Eskimo)", "3": "Caucasian (European)",
        "4": "Caucasian (Indian)", "5": "Caucasian (Middle East)",
        "6": "Caucasian (North African, Other)", "7": "Indigenous Australian",
        "8": "Native American", "9": "North East Asian (Mongol, Tibetan, Korean Japanese, etc)",
        "10": "Pacific (Polynesian, Micronesian, etc)",
        "11": "South East Asian (Chinese, Thai, Malay, Filipino, etc)",
        "12": "West African, Bushmen, Ethiopian", "13": "Other"}


def load_codebook(path: Path) -> dict[str, str]:
    """item text (lowercased) -> column name, from BIG5/codebook.txt."""
    code = {}
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^([ENACO]\d+)\t(.+?)\s*$", line)
        if m:
            code[m.group(2).strip().lower()] = m.group(1)
    return code


def big_five_scores(answers: dict[str, int]) -> dict[str, int]:
    out = {}
    for d in DIMS:
        total = 0
        for i in range(1, 11):
            x = answers[f"{d}{i}"]
            total += (6 - x) if i in _REVERSED[d] else x
        out[DIM_NAME[d]] = total
    return out


def demographics_of(row: dict) -> dict:
    return {
        "age": int(row["age"]),
        "gender": GENDER.get(row["gender"], "person"),
        "country": row["country"],
        "race": RACE.get(row["race"], "Other"),
        "handedness": HAND.get(row["hand"], "Right-handed"),
        "native_english": row["engnat"] == "1",
    }


def load_track_a(big5_csv: Path, codebook: Path, masked_jsonl: Path) -> list[dict]:
    code = load_codebook(codebook)
    with open(big5_csv, encoding="utf-8", errors="replace") as f:
        raw = list(csv.DictReader(f, delimiter="\t"))
    vecs = [tuple(int(r[c]) if r[c].isdigit() else -1 for c in COLS) for r in raw]
    subjects = []
    for line in Path(masked_jsonl).read_text().splitlines():
        rec = json.loads(line)
        known = {COLS.index(code[t.strip().lower()]): int(a)
                 for t, a in re.findall(r"\d+\. ([^\n]+)\nAnswer: \[(\d)\]", rec["user"])}
        hits = [i for i, v in enumerate(vecs) if all(v[k] == a for k, a in known.items())]
        if len(hits) != 1:
            continue
        i = hits[0]
        answers = dict(zip(COLS, vecs[i]))
        subjects.append({
            "subject_id": str(i),
            "target_item": rec["metadata"]["target_item"],
            "target_answer": int(rec["assistant"].strip("[]")),
            "demographics": demographics_of(raw[i]),
            "big_five": big_five_scores(answers),
            "answers": answers,
            "record": rec,
        })
    return subjects


def load_track_b(acrossgame_jsonl: Path) -> list[dict]:
    subjects = []
    for line in Path(acrossgame_jsonl).read_text().splitlines():
        rec = json.loads(line)
        blocks = re.findall(r"\n\d+\. ([^\n]+)\n- Game instruction: (.*?)\n- Your choice: \[([^\]]+)\]",
                            rec["user"], flags=re.S)
        subjects.append({
            "subject_id": rec["metadata"]["user_id"],
            "target_game": rec["metadata"]["target_game"],
            "history_games": rec["metadata"]["history_games"],
            "play_history": [{"game_label": b[0].strip(), "instruction": b[1].strip(), "choice": b[2].strip()}
                             for b in blocks],
            "target_answer": rec["assistant"].strip("[]"),
            "record": rec,
            # "type_vector": filled in by type_vector.fit_subject()
        })
    return subjects
