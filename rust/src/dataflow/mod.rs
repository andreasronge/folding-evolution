/// Dataflow evaluation: an alternative to the sequential chemistry pipeline.
///
/// Instead of building ASTs through 5 passes of exclusive bonding,
/// the folded grid IS the program. Values propagate through cells via
/// broadcast message passing over K rounds.
///
/// Key differences from chemistry pipeline:
/// - Broadcasting: multiple cells can read the same neighbor's output
/// - Vectorized: `get` maps element-wise over lists-of-dicts
/// - No closures: filter uses boolean masks from comparator chains
/// - Wildcards act as relay cells, extending connectivity
///
/// This is a new representation for comparison, not a port of the chemistry.

pub mod grid;
pub mod evaluate;
