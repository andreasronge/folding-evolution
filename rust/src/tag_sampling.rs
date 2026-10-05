//! Sampling-only TAG evaluator, matching tagged.py with threshold 0 and NOP slots.
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use rayon::prelude::*;
#[derive(Clone, Copy)]
enum V {
    Int(i64),
    List(bool),
    Chars,
}
fn pi(s: &mut Vec<V>) -> i64 {
    if matches!(s.last(), Some(V::Int(_))) {
        if let Some(V::Int(x)) = s.pop() {
            return x;
        }
    }
    0
}
fn pl(s: &mut Vec<V>) -> bool {
    if matches!(s.last(), Some(V::List(_))) {
        if let Some(V::List(x)) = s.pop() {
            return x;
        }
    }
    false
}
struct Tape<'a> {
    g: &'a [u8],
    l: usize,
    runs: Vec<(u8, usize, usize)>,
}
impl<'a> Tape<'a> {
    fn new(g: &'a [u8]) -> Self {
        let l = g.len() / 2;
        let starts: Vec<usize> = (0..l).filter(|&i| g[i] == 20).collect();
        let runs = starts
            .iter()
            .enumerate()
            .map(|(k, &i)| (g[l + i], i + 1, *starts.get(k + 1).unwrap_or(&l)))
            .collect();
        Self { g, l, runs }
    }
    fn tag(&self, tag: u8, x: &[i64], d: usize, v: u64, memo: &mut [Option<i64>; 64]) -> i64 {
        let mut out = None;
        for (k, &(t, _, _)) in self.runs.iter().enumerate() {
            if t == tag {
                let a = self.run(k, x, d, v, memo);
                out = Some(out.map_or(a, |b: i64| b.max(a)));
            }
        }
        out.unwrap_or(0)
    }
    fn run(&self, k: usize, x: &[i64], d: usize, v: u64, memo: &mut [Option<i64>; 64]) -> i64 {
        if let Some(a) = memo[k] {
            return a;
        }
        if d > 8 || v & (1u64 << k) != 0 {
            return 0;
        }
        let (_, start, end) = self.runs[k];
        let mut s = Vec::with_capacity(end - start + 2);
        for i in start..end {
            match self.g[i] {
                0 | 12 | 13 => {}
                1 => s.push(V::List(true)),
                2 | 19 => s.push(V::Int(0)),
                3 => s.push(V::Int(1)),
                15 => s.push(V::Int(2)),
                16 => s.push(V::Int(5)),
                4 => s.push(V::Chars),
                14 => {
                    if matches!(s.last(), Some(V::Chars)) {
                        s.pop();
                    }
                    s.push(V::List(false));
                }
                5 | 11 | 6 | 18 => {
                    let has = pl(&mut s);
                    let a = if !has {
                        0
                    } else {
                        match self.g[i] {
                            6 => i64::from(x.iter().any(|&a| a != 0)),
                            18 => *x.iter().max().unwrap_or(&0),
                            _ => x.iter().fold(0i64, |a, &b| a.wrapping_add(b)),
                        }
                    };
                    s.push(V::Int(a));
                }
                7 | 8 => {
                    let b = pi(&mut s);
                    let a = pi(&mut s);
                    s.push(V::Int(if self.g[i] == 7 {
                        a.wrapping_add(b)
                    } else {
                        i64::from(a > b)
                    }));
                }
                9 => {
                    let a = *s.last().unwrap_or(&V::Int(0));
                    if s.is_empty() {
                        s.push(a);
                    }
                    s.push(a);
                }
                10 => {
                    let b = s.pop().unwrap_or(V::Int(0));
                    let a = s.pop().unwrap_or(V::Int(0));
                    s.push(b);
                    s.push(a);
                }
                17 => {
                    if s.len() < 3 {
                        for _ in 0..3 {
                            pi(&mut s);
                        }
                        s.push(V::Int(0));
                    } else {
                        let c = pi(&mut s);
                        let t = pi(&mut s);
                        let e = pi(&mut s);
                        s.push(V::Int(if c > 0 { t } else { e }));
                    }
                }
                21 => s.push(V::Int(self.tag(
                    self.g[self.l + i],
                    x,
                    d + 1,
                    v | (1u64 << k),
                    memo,
                ))),
                _ => unreachable!(),
            }
        }
        let out = if let Some(V::Int(a)) = s.last() {
            *a
        } else {
            0
        };
        if v == 0 {
            memo[k] = Some(out);
        }
        out
    }
}
fn validate(g: &[u8], l: usize, x: &[Vec<i64>]) -> PyResult<()> {
    if l == 0 || l > 64 || g.len() % (2 * l) != 0 || x.iter().any(|a| a.len() != 4) {
        return Err(PyValueError::new_err(
            "require L<=64, whole tapes, four-digit inputs",
        ));
    }
    for r in g.chunks_exact(2 * l) {
        if r[..l].iter().any(|&a| a >= 22) || r[l..].iter().any(|&a| a >= 64) {
            return Err(PyValueError::new_err("invalid op/tag"));
        }
    }
    Ok(())
}
/// Early task rejection; shared outputs are evaluated once per input.
#[pyfunction]
pub fn rust_tag_screen(
    py: Python<'_>,
    g: Vec<u8>,
    l: usize,
    x: Vec<Vec<i64>>,
    y: Vec<Vec<i64>>,
) -> PyResult<Vec<(usize, u64)>> {
    validate(&g, l, &x)?;
    if y.is_empty() || y.len() > 63 || y.iter().any(|a| a.len() != x.len()) {
        return Err(PyValueError::new_err("invalid labels"));
    }
    Ok(py.allow_threads(|| {
        g.par_chunks_exact(2 * l)
            .enumerate()
            .filter_map(|(i, r)| {
                let t = Tape::new(r);
                let mut m = (1u64 << y.len()) - 1;
                for (j, a) in x.iter().enumerate() {
                    let p = t.tag(0, a, 0, 0, &mut [None; 64]);
                    for (k, b) in y.iter().enumerate() {
                        if m & (1u64 << k) != 0 && p != b[j] {
                            m &= !(1u64 << k);
                        }
                    }
                    if m == 0 {
                        return None;
                    }
                }
                Some((i, m))
            })
            .collect()
    }))
}
#[pyfunction]
pub fn rust_tag_outputs(
    py: Python<'_>,
    g: Vec<u8>,
    l: usize,
    x: Vec<Vec<i64>>,
) -> PyResult<Vec<Vec<i64>>> {
    validate(&g, l, &x)?;
    Ok(py.allow_threads(|| {
        g.par_chunks_exact(2 * l)
            .map(|r| {
                let t = Tape::new(r);
                x.iter()
                    .map(|a| t.tag(0, a, 0, 0, &mut [None; 64]))
                    .collect()
            })
            .collect()
    }))
}
