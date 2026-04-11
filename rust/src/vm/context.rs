/// Python dict -> Rust context conversion.

use std::collections::HashMap;
use std::sync::Arc;

use pyo3::prelude::*;
use pyo3::types::{PyBool, PyDict, PyFloat, PyList, PyString};

use super::value::Value;

/// Pre-indexed evaluation context.
/// data_sources: [products, employees, orders, expenses]
#[derive(Clone)]
pub struct EvalContext {
    pub data_sources: [Value; 4],
}

impl EvalContext {
    pub fn from_py_dict(dict: &Bound<'_, PyDict>) -> PyResult<Self> {
        let sources = ["products", "employees", "orders", "expenses"];
        let mut data_sources = [Value::Nil, Value::Nil, Value::Nil, Value::Nil];

        for (i, key) in sources.iter().enumerate() {
            if let Some(val) = dict.get_item(key)? {
                data_sources[i] = py_to_value(&val)?;
            }
        }

        Ok(EvalContext { data_sources })
    }
}

/// Convert a Python object to a Rust Value.
pub fn py_to_value(obj: &Bound<'_, PyAny>) -> PyResult<Value> {
    if obj.is_none() {
        return Ok(Value::Nil);
    }
    // Check bool before int (bool is a subclass of int in Python)
    if let Ok(b) = obj.downcast::<PyBool>() {
        return Ok(Value::Bool(b.is_true()));
    }
    if let Ok(i) = obj.extract::<i64>() {
        return Ok(Value::Int(i));
    }
    if let Ok(f) = obj.downcast::<PyFloat>() {
        return Ok(Value::Int(f.value() as i64));
    }
    if let Ok(s) = obj.downcast::<PyString>() {
        return Ok(Value::Str(Arc::from(s.to_str()?)));
    }
    if let Ok(list) = obj.downcast::<PyList>() {
        let items: Vec<Value> = list
            .iter()
            .map(|item| py_to_value(&item))
            .collect::<PyResult<_>>()?;
        return Ok(Value::List(Arc::new(items)));
    }
    if let Ok(dict) = obj.downcast::<PyDict>() {
        let mut map = HashMap::new();
        for (k, v) in dict.iter() {
            let key: Arc<str> = Arc::from(k.extract::<&str>()?);
            let val = py_to_value(&v)?;
            map.insert(key, val);
        }
        return Ok(Value::Dict(Arc::new(map)));
    }
    Ok(Value::Nil)
}

/// Convert a Rust Value back to a Python object.
pub fn value_to_py(py: Python<'_>, val: &Value) -> PyResult<PyObject> {
    match val {
        Value::Nil | Value::Error => Ok(py.None()),
        Value::Bool(b) => Ok(b.to_object(py)),
        Value::Int(i) => Ok(i.to_object(py)),
        Value::Str(s) => Ok(s.to_object(py)),
        Value::List(items) => {
            let py_items: Vec<PyObject> = items
                .iter()
                .map(|v| value_to_py(py, v))
                .collect::<PyResult<_>>()?;
            Ok(PyList::new_bound(py, &py_items).to_object(py))
        }
        Value::Dict(map) => {
            let dict = PyDict::new_bound(py);
            for (k, v) in map.iter() {
                dict.set_item(k.as_ref(), value_to_py(py, v)?)?;
            }
            Ok(dict.to_object(py))
        }
    }
}
