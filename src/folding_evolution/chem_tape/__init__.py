"""Chemistry-tape GP — a 1D token-tape substrate with bond-based decode.

A third research track alongside folding and CA. The tape is a length-L byte
array; each cell's low 4 bits is a token id. A fixed chemistry rule computes
bonds between adjacent active cells; the longest bonded run decodes as an RPN
stack program.

See `docs/chem-tape/architecture.md` for the v1 specification.
"""
