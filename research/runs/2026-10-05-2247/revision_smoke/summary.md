# Composition-bank feasibility

Outcome U: Unresolved: missing complete search or top-up data.

Raw per-seed data: searches.jsonl. Full metrics and selection: result.json.
This feasibility study does not test learned transfer.
Cells share seeds and are correlated; cross-cell comparisons must retain pairing.
Bigram overlap includes all nine canonical cells, including rejected cells.

Structural headroom (ignoring tractability; partial; None denotes an unresolved median):

- SM-ADD, Sm-DADD, Mm-SEL: lacks headroom; F medians=[256, 7680, 6400]; G medians=[256, 2048, 1024]
- SM-ADD, Sm-SEL, Mm-DADD: lacks headroom; F medians=[256, None, 5376]; G medians=[256, 512, 1024]
- SM-DADD, Sm-ADD, Mm-SEL: lacks headroom; F medians=[2816, 1024, 6400]; G medians=[1024, 256, 1024]
- SM-DADD, Sm-SEL, Mm-ADD: lacks headroom; F medians=[2816, None, 2816]; G medians=[1024, 512, 768]

Every structural candidate lacks fixed-control headroom. G is a generic grammar within this canonical family. This diagnostic does not change the pre-stated outcome order.
