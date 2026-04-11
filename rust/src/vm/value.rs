/// Runtime value type for the stack machine VM.

use std::collections::HashMap;
use std::fmt;
use std::sync::Arc;

#[derive(Clone, Debug)]
pub enum Value {
    Nil,
    Bool(bool),
    Int(i64),
    Str(Arc<str>),
    List(Arc<Vec<Value>>),
    Dict(Arc<HashMap<Arc<str>, Value>>),
    /// Represents a Python TypeError/exception that propagates upward.
    /// Any operation receiving Error as input must produce Error,
    /// matching Python's exception propagation semantics.
    /// Converted to Nil at the top-level execute() boundary.
    Error,
}

impl Value {
    pub fn is_truthy(&self) -> bool {
        match self {
            Value::Nil => false,
            Value::Bool(b) => *b,
            Value::Int(0) => false,
            Value::Int(_) => true,
            Value::List(l) => !l.is_empty(),
            Value::Error => false, // should not be reached (propagation)
            _ => true,
        }
    }

    pub fn is_error(&self) -> bool {
        matches!(self, Value::Error)
    }
}

/// Structural equality matching Python's == semantics.
/// In Python, True == 1 and False == 0, so we coerce bool to int for comparison.
pub fn values_equal(a: &Value, b: &Value) -> bool {
    match (a, b) {
        (Value::Nil, Value::Nil) => true,
        (Value::Bool(x), Value::Bool(y)) => x == y,
        (Value::Int(x), Value::Int(y)) => x == y,
        // Python: True == 1, False == 0
        (Value::Bool(x), Value::Int(y)) => (*x as i64) == *y,
        (Value::Int(x), Value::Bool(y)) => *x == (*y as i64),
        (Value::Str(x), Value::Str(y)) => x == y,
        (Value::List(x), Value::List(y)) => {
            x.len() == y.len() && x.iter().zip(y.iter()).all(|(a, b)| values_equal(a, b))
        }
        (Value::Dict(x), Value::Dict(y)) => {
            if x.len() != y.len() {
                return false;
            }
            x.iter().all(|(k, v)| y.get(k).map_or(false, |v2| values_equal(v, v2)))
        }
        _ => false,
    }
}

/// repr-like string for data-dependence gate comparison.
pub fn value_repr(v: &Value) -> String {
    match v {
        Value::Nil | Value::Error => "None".to_string(),
        Value::Bool(b) => if *b { "True".to_string() } else { "False".to_string() },
        Value::Int(i) => i.to_string(),
        Value::Str(s) => format!("'{}'", s),
        Value::List(items) => {
            let inner: Vec<String> = items.iter().map(value_repr).collect();
            format!("[{}]", inner.join(", "))
        }
        Value::Dict(map) => {
            let mut pairs: Vec<_> = map.iter().collect();
            pairs.sort_by_key(|(k, _)| k.clone());
            let inner: Vec<String> = pairs.iter()
                .map(|(k, v)| format!("'{}': {}", k, value_repr(v)))
                .collect();
            format!("{{{}}}", inner.join(", "))
        }
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", value_repr(self))
    }
}
