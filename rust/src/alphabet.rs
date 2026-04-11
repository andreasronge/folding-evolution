/// Alphabet: maps genotype characters to fragment types and fold instructions.
/// Table-driven — modify these tables to change the mapping.

use crate::types::*;
use crate::chemistry::Fragment;

/// Returns (Fragment, FoldInstruction) for a genotype character.
pub fn decode(ch: u8) -> (Fragment, FoldInstruction) {
    let frag = to_fragment(ch);
    let fold = fold_instruction(ch);
    (frag, fold)
}

pub fn to_fragment(ch: u8) -> Fragment {
    match ch {
        // Functions (A-I)
        b'A' => Fragment::Fn(Op::Filter),
        b'B' => Fragment::Fn(Op::Count),
        b'C' => Fragment::Fn(Op::Map),
        b'D' => Fragment::Fn(Op::Get),
        b'E' => Fragment::Fn(Op::Reduce),
        b'F' => Fragment::Fn(Op::GroupBy),
        b'G' => Fragment::Fn(Op::Set),
        b'H' => Fragment::Fn(Op::Contains),
        b'I' => Fragment::Fn(Op::First),
        // Comparators (J-L)
        b'J' => Fragment::Comparator(Op::Plus),
        b'K' => Fragment::Comparator(Op::Gt),
        b'L' => Fragment::Comparator(Op::Lt),
        b'M' => Fragment::Comparator(Op::Eq),
        // Connectives (N-P)
        b'N' => Fragment::Connective(Op::And),
        b'O' => Fragment::Connective(Op::Or),
        b'P' => Fragment::Connective(Op::Not),
        // Function wrappers (Q-R)
        b'Q' => Fragment::Fn(Op::Fn),
        b'R' => Fragment::Fn(Op::Let),
        // Data sources (S-V)
        b'S' => Fragment::DataSource(DataSource::Products),
        b'T' => Fragment::DataSource(DataSource::Employees),
        b'U' => Fragment::DataSource(DataSource::Orders),
        b'V' => Fragment::DataSource(DataSource::Expenses),
        // Structural / conditional (W-Y)
        b'W' => Fragment::Fn(Op::Match),
        b'X' => Fragment::Fn(Op::If),
        b'Y' => Fragment::Fn(Op::Assoc),
        // Spacer
        b'Z' => Fragment::Spacer,
        // Field keys (a-h)
        b'a' => Fragment::FieldKey(FieldKey::Price),
        b'b' => Fragment::FieldKey(FieldKey::Status),
        b'c' => Fragment::FieldKey(FieldKey::Department),
        b'd' => Fragment::FieldKey(FieldKey::Id),
        b'e' => Fragment::FieldKey(FieldKey::Name),
        b'f' => Fragment::FieldKey(FieldKey::Amount),
        b'g' => Fragment::FieldKey(FieldKey::Category),
        b'h' => Fragment::FieldKey(FieldKey::EmployeeId),
        // Collection-returning functions (i-l)
        b'i' => Fragment::Fn(Op::Reverse),
        b'j' => Fragment::Fn(Op::Sort),
        b'k' => Fragment::Fn(Op::Rest),
        b'l' => Fragment::Fn(Op::Last),
        // Wildcards (m-z)
        b'm'..=b'z' => Fragment::Wildcard,
        // Digits (0-9) -> literals 0, 100, 200, ..., 900
        b'0'..=b'9' => Fragment::Literal((ch - b'0') as i64 * 100),
        _ => Fragment::Spacer,
    }
}

pub fn fold_instruction(ch: u8) -> FoldInstruction {
    match ch {
        b'W' => FoldInstruction::Straight,
        b'X' => FoldInstruction::Left,
        b'Y' => FoldInstruction::Right,
        b'Z' => FoldInstruction::Reverse,
        b'a'..=b'z' => FoldInstruction::Straight,
        b'0'..=b'9' => FoldInstruction::Straight,
        b'A'..=b'V' => FoldInstruction::Left,
        _ => FoldInstruction::Straight,
    }
}
