"""Taller evaluable"""

# pylint: disable=broad-exception-raised
# pylint: disable=import-error

from __future__ import annotations

import csv
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterable

#
# ORQUESTADOR:
#
def run():
    """Orquestador"""

    input_path = os.path.join("files", "input", "tips.csv")

    rows = _read_tips_csv(input_path)

    _write_query_output("files/query_1", _query_1_count_by_day(rows))
    _write_query_output("files/query_2", _query_2_avg_tip_by_sex(rows))
    _write_query_output("files/query_3", _query_3_max_total_bill_by_day(rows))
    _write_query_output("files/query_4", _query_4_count_by_smoker(rows))
    _write_query_output("files/query_5", _query_5_avg_tip_pct_by_day(rows))


@dataclass(frozen=True)
class TipRow:
    total_bill: float
    tip: float
    sex: str
    smoker: str
    day: str
    time: str
    size: int


def _read_tips_csv(path: str) -> list[TipRow]:
    if not os.path.exists(path):
        raise Exception(f"Input file not found: {path}")

    rows: list[TipRow] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            rows.append(
                TipRow(
                    total_bill=float(raw["total_bill"]),
                    tip=float(raw["tip"]),
                    sex=str(raw["sex"]),
                    smoker=str(raw["smoker"]),
                    day=str(raw["day"]),
                    time=str(raw["time"]),
                    size=int(raw["size"]),
                )
            )
    return rows


def _write_query_output(output_dir: str, lines: Iterable[str]) -> None:
    os.makedirs(output_dir, exist_ok=True)

    part_path = os.path.join(output_dir, "part-00000")
    success_path = os.path.join(output_dir, "_SUCCESS")

    with open(part_path, "w", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(line.rstrip("\n"))
            f.write("\n")

    # La existencia de este archivo suele indicar un job completado.
    with open(success_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("")


def _group_reduce(
    rows: Iterable[TipRow],
    key_fn: Callable[[TipRow], str],
    value_fn: Callable[[TipRow], float],
    reduce_fn: Callable[[list[float]], float],
) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        buckets[key_fn(r)].append(value_fn(r))
    return {k: reduce_fn(vs) for k, vs in buckets.items()}


def _avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _query_1_count_by_day(rows: list[TipRow]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r.day] += 1
    return [f"{day}\t{counts[day]}" for day in sorted(counts)]


def _query_2_avg_tip_by_sex(rows: list[TipRow]) -> list[str]:
    avgs = _group_reduce(rows, key_fn=lambda r: r.sex, value_fn=lambda r: r.tip, reduce_fn=_avg)
    return [f"{sex}\t{avgs[sex]:.2f}" for sex in sorted(avgs)]


def _query_3_max_total_bill_by_day(rows: list[TipRow]) -> list[str]:
    maxes: dict[str, float] = {}
    for r in rows:
        if r.day not in maxes or r.total_bill > maxes[r.day]:
            maxes[r.day] = r.total_bill
    return [f"{day}\t{maxes[day]:.2f}" for day in sorted(maxes)]


def _query_4_count_by_smoker(rows: list[TipRow]) -> list[str]:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r.smoker] += 1
    return [f"{smoker}\t{counts[smoker]}" for smoker in sorted(counts)]


def _query_5_avg_tip_pct_by_day(rows: list[TipRow]) -> list[str]:
    pct_by_day: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r.total_bill <= 0:
            continue
        pct_by_day[r.day].append((r.tip / r.total_bill) * 100.0)

    avgs = {day: _avg(pcts) for day, pcts in pct_by_day.items()}
    return [f"{day}\t{avgs[day]:.2f}" for day in sorted(avgs)]

if __name__ == "__main__":

    run()