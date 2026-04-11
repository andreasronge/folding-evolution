/// Core enums for the folding pipeline.
/// These are finite sets — no strings in the hot path.

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Op {
    // Functions
    Filter, Count, Map, Get, Reduce, GroupBy, Set, Contains,
    First, Reverse, Sort, Rest, Last,
    Fn, Let, Assoc, Match, If,
    // Comparators
    Plus, Gt, Lt, Eq,
    // Connectives
    And, Or, Not,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum FieldKey {
    Price, Status, Department, Id, Name, Amount, Category, EmployeeId,
    Pattern,  // used by match bond in pass_conditional
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum DataSource {
    Products, Employees, Orders, Expenses,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Direction {
    Up, Down, Left, Right,
}

impl Direction {
    pub fn turn_left(self) -> Direction {
        match self {
            Direction::Right => Direction::Up,
            Direction::Up => Direction::Left,
            Direction::Left => Direction::Down,
            Direction::Down => Direction::Right,
        }
    }

    pub fn turn_right(self) -> Direction {
        match self {
            Direction::Right => Direction::Down,
            Direction::Down => Direction::Left,
            Direction::Left => Direction::Up,
            Direction::Up => Direction::Right,
        }
    }

    pub fn reverse(self) -> Direction {
        match self {
            Direction::Right => Direction::Left,
            Direction::Left => Direction::Right,
            Direction::Up => Direction::Down,
            Direction::Down => Direction::Up,
        }
    }

    pub fn advance(self, x: i32, y: i32) -> (i32, i32) {
        match self {
            Direction::Right => (x + 1, y),
            Direction::Left => (x - 1, y),
            Direction::Up => (x, y - 1),
            Direction::Down => (x, y + 1),
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum FoldInstruction {
    Left, Right, Straight, Reverse,
}

impl Op {
    pub fn to_str(self) -> &'static str {
        match self {
            Op::Filter => "filter", Op::Count => "count", Op::Map => "map",
            Op::Get => "get", Op::Reduce => "reduce", Op::GroupBy => "group_by",
            Op::Set => "set", Op::Contains => "contains?",
            Op::First => "first", Op::Reverse => "reverse", Op::Sort => "sort",
            Op::Rest => "rest", Op::Last => "last",
            Op::Fn => "fn", Op::Let => "let", Op::Assoc => "assoc",
            Op::Match => "match", Op::If => "if",
            Op::Plus => "+", Op::Gt => ">", Op::Lt => "<", Op::Eq => "=",
            Op::And => "and", Op::Or => "or", Op::Not => "not",
        }
    }
}

impl FieldKey {
    pub fn to_str(self) -> &'static str {
        match self {
            FieldKey::Price => "price", FieldKey::Status => "status",
            FieldKey::Department => "department", FieldKey::Id => "id",
            FieldKey::Name => "name", FieldKey::Amount => "amount",
            FieldKey::Category => "category", FieldKey::EmployeeId => "employee_id",
            FieldKey::Pattern => "pattern",
        }
    }
}

impl DataSource {
    pub fn to_str(self) -> &'static str {
        match self {
            DataSource::Products => "products", DataSource::Employees => "employees",
            DataSource::Orders => "orders", DataSource::Expenses => "expenses",
        }
    }
}
