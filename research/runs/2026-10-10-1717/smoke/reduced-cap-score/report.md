# Same-alphabet crossed family preference

SMOKE ONLY: development cells.

|Capped-cost contrast|Point|95% build/seed interval|
|---|---:|---:|
|P_DG|1.116|[1.000, 1.553]|
|P_TS|0.736|[0.507, 1.000]|
|I|0.907|[0.712, 1.143]|
|G4/D_DG|1.116|[1.000, 1.553]|
|G4/T_DG|1.000|[1.000, 1.000]|
|G4/D_TS|1.358|[1.000, 1.973]|
|G4/T_TS|1.000|[1.000, 1.000]|

{
  "interaction": "geometric interaction below1.5 margin",
  "directions": {
    "P_DG": "unresolved direction",
    "P_TS": "unresolved direction"
  },
  "reciprocal": false,
  "dominant_bias": null,
  "dominant_bias_with_interaction": false,
  "own_family_useful": false,
  "family_specific_acquisition_candidate": false,
  "shared_bias_candidate": false,
  "next": "strategy"
}

Penalty-sensitive: False.

Only a constant multiplicative advantage cancels from I. Unresolved directions remain unresolved; exclude only interaction above the1.5 margin. Own-family usefulness and directions accompany the interaction.

Solves: {'DG': {'G4': {'solved': 0, 'attempts': 16}, 'D': {'solved': 1, 'attempts': 16}, 'T': {'solved': 0, 'attempts': 16}}, 'TS': {'G4': {'solved': 0, 'attempts': 16}, 'D': {'solved': 4, 'attempts': 16}, 'T': {'solved': 0, 'attempts': 16}}}

external fitting and literal fragments on fixed same-alphabet rosters; DG development bank; no inheritance, competitive-baseline, pure ADD-placement or broad fresh-bank claim

Per-cell/build costs, retained fallbacks, acquisition economics and a conditional resolution price are in result.json/builds.json/preparation.json. No arithmetic saving means no demonstrated break-even.

Closest precedents: [PIPE](https://pubmed.ncbi.nlm.nih.gov/10021756/) and [Wild & Porter (2022)](https://eprints.lancs.ac.uk/id/eprint/174982/?template=browse).
