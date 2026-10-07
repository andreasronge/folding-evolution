"""Regenerate portable 2129 artifacts from the two hash-pinned source runs."""

import gzip
import hashlib
import json
from pathlib import Path

from experiments.chem_tape.solver_corpus_fit import validate_table

ROOT = Path("/Users/andreas/developer/folding-evolution/experiments/output/2026-10-07")
SOURCES = {
    "1707": (
        "2026-10-07-1707-solver-corpus-context",
        {
            "config.json": "9fd82efea1f588b50a4d513242aee4a73b891e17da056459c4fe02e022dc14fb",
            "corpora.json": "90b20c6f8bb60bd082141b358453cca85583ce92228fc4e88f432647dcf0747c",
            "search.jsonl": "98475848d168834195343a84991745b6624d3bf8a8a4cad53bced7753cdc7223",
        },
    ),
    "1924": (
        "2026-10-07-1924-solver-feedback",
        {
            "config.json": "72c9d04a5af19e58932823e5dedaed70b9a25ae9ce34e2bbfbf3e951701aa9c3",
            "corpora.json": "49e54c74d95a924dd93c8e234f469b46f765fd487ea0e335d26d266d8fcefc43",
            "search.jsonl": "d57267f8caf3c2b56cc3b19512a8615c68d05525a01e9714b059f7eac2d30824",
        },
    ),
}
DATA = Path(__file__).with_name("data") / "context_increment_2129"


def main():
    sources = {}
    for label, (directory, hashes) in SOURCES.items():
        source = {}
        for name, digest in hashes.items():
            raw = (ROOT / directory / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError(f"{label}/{name} hash mismatch")
            source[name] = (
                [json.loads(line) for line in raw.splitlines()]
                if name.endswith("jsonl")
                else json.loads(raw)
            )
        sources[label] = source
    tables = {}
    for tid, original in sources["1707"]["corpora.json"].items():
        feedback = sources["1924"]["corpora.json"][tid]
        if feedback["C"] != original["tables"]["C"]:
            raise ValueError("parent C table mismatch")
        fits = {
            "T1": (original, "T"),
            "C1": (original, "C"),
            "T2": (feedback["C2"], "T"),
            "C2": (feedback["C2"], "C"),
        }
        record = dict(
            family=original["family"], index=original["index"], tables={}, hashes={}
        )
        for arm, (fit, source_arm) in fits.items():
            table, digest = fit["tables"][source_arm], fit["fit"]["hashes"][source_arm]
            if validate_table(table) != digest:
                raise ValueError("saved fit hash mismatch")
            record["tables"][arm], record["hashes"][arm] = table, digest
        tables[tid] = record
    rows = []
    for row in sources["1924"]["search.jsonl"]:
        if row["phase"] in ("training", "holdout") and row["arm"] in ("C", "C2"):
            row = dict(row)
            row["arm"] = "C1" if row["arm"] == "C" else "C2"
            rows.append(row)
    rows.sort(
        key=lambda r: tuple(
            r[k] for k in ("phase", "family", "corpus", "cell", "seed", "arm")
        )
    )
    files = {
        "tables.json": (json.dumps(tables, indent=2) + "\n").encode(),
        "context_rows.jsonl.gz": gzip.compress(
            "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows).encode(),
            mtime=0,
        ),
    }
    provenance = dict(
        sources=SOURCES,
        source_configs={k: v["config.json"] for k, v in sources.items()},
        context_row_count=len(rows),
        artifact_hashes={
            n: hashlib.sha256(raw).hexdigest() for n, raw in files.items()
        },
    )
    files["provenance.json"] = (json.dumps(provenance, indent=2) + "\n").encode()
    DATA.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        (DATA / name).write_bytes(raw)
    print(hashlib.sha256(files["provenance.json"]).hexdigest())


if __name__ == "__main__":
    main()
