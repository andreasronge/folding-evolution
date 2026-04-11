/// Bytecode instruction set and compiler (AstNode -> Bytecode).

use std::collections::HashMap;
use std::sync::Arc;

use crate::ast::AstNode;
use crate::types::Op;

/// Stack machine instructions.
#[derive(Clone, Debug)]
pub enum Inst {
    PushNil,
    PushInt(i64),
    PushStr(u16), // index into string constant pool
    LoadData(u8), // push context.data_sources[idx]
    LoadLocal(u16),

    // Collection ops
    Count,
    First,
    Rest,
    GetField, // pop key, pop dict -> push dict[key]

    // Arithmetic & comparison
    Add,
    Sub,
    Gt,
    Lt,
    Eq,
    Not,

    /// Pop n values; push Error if any was Error, else push Nil.
    /// Used for unsupported ops: we compile their args (for error propagation)
    /// then discard the values since the op itself returns None in Python.
    DiscardArgs(u8),

    // Control flow
    JumpIfFalse(u16),
    Jump(u16),

    // Higher-order with inline closure body.
    // FilterBegin(param_slot, end_ip): pop data list, iterate elements,
    // store each in locals[param_slot], execute body, filter by truthiness.
    FilterBegin(u16, u16),
    FilterEnd,
    MapBegin(u16, u16),
    MapEnd,

    Return,
}

/// Compiled program.
#[derive(Clone, Debug)]
pub struct Bytecode {
    pub instructions: Vec<Inst>,
    pub string_pool: Vec<Arc<str>>,
    pub source: String,
    pub bond_count: usize,
}

/// Compiler state.
struct Compiler {
    instructions: Vec<Inst>,
    string_pool: Vec<Arc<str>>,
    string_index: HashMap<Arc<str>, u16>,
    local_count: u16,
    scopes: Vec<HashMap<String, u16>>,
}

impl Compiler {
    fn new() -> Self {
        Compiler {
            instructions: Vec::new(),
            string_pool: Vec::new(),
            string_index: HashMap::new(),
            local_count: 0,
            scopes: vec![HashMap::new()],
        }
    }

    fn emit(&mut self, inst: Inst) -> usize {
        let idx = self.instructions.len();
        self.instructions.push(inst);
        idx
    }

    fn intern_string(&mut self, s: &str) -> u16 {
        let arc: Arc<str> = Arc::from(s);
        if let Some(&idx) = self.string_index.get(&arc) {
            return idx;
        }
        let idx = self.string_pool.len() as u16;
        self.string_pool.push(arc.clone());
        self.string_index.insert(arc, idx);
        idx
    }

    fn resolve_local(&self, name: &str) -> Option<u16> {
        for scope in self.scopes.iter().rev() {
            if let Some(&slot) = scope.get(name) {
                return Some(slot);
            }
        }
        None
    }

    fn alloc_local(&mut self) -> u16 {
        let slot = self.local_count;
        self.local_count += 1;
        slot
    }

    fn compile_node(&mut self, node: &AstNode) {
        match node {
            AstNode::Literal(v) => {
                self.emit(Inst::PushInt(*v));
            }
            AstNode::Keyword(k) => {
                let idx = self.intern_string(k.to_str());
                self.emit(Inst::PushStr(idx));
            }
            AstNode::NsSymbol { ns, name } => {
                if *ns == "data" {
                    let ds_idx = match *name {
                        "products" => 0u8,
                        "employees" => 1,
                        "orders" => 2,
                        "expenses" => 3,
                        _ => {
                            self.emit(Inst::PushNil);
                            return;
                        }
                    };
                    self.emit(Inst::LoadData(ds_idx));
                } else {
                    self.emit(Inst::PushNil);
                }
            }
            AstNode::SymbolStr(s) => {
                if let Some(slot) = self.resolve_local(s) {
                    self.emit(Inst::LoadLocal(slot));
                } else {
                    self.emit(Inst::PushNil);
                }
            }
            AstNode::Symbol(op) => {
                // Bare symbol as value reference (e.g., variable "x" encoded as Op)
                let name = op.to_str();
                if let Some(slot) = self.resolve_local(name) {
                    self.emit(Inst::LoadLocal(slot));
                } else {
                    self.emit(Inst::PushNil);
                }
            }
            AstNode::ListExpr(items) => {
                self.compile_list_expr(items);
            }
        }
    }

    fn compile_list_expr(&mut self, items: &[AstNode]) {
        if items.is_empty() {
            self.emit(Inst::PushNil);
            return;
        }

        let op = &items[0];
        let args = &items[1..];

        match op {
            AstNode::Symbol(Op::Fn) => self.compile_fn(args),
            AstNode::Symbol(Op::If) => self.compile_if(args),
            AstNode::Symbol(Op::And) => self.compile_and(args),
            AstNode::Symbol(Op::Or) => self.compile_or(args),
            AstNode::Symbol(Op::Filter) => self.compile_filter(args),
            AstNode::Symbol(Op::Map) => self.compile_map(args),
            AstNode::Symbol(Op::Count) => {
                if args.is_empty() { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.emit(Inst::Count);
            }
            AstNode::Symbol(Op::First) => {
                if args.is_empty() { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.emit(Inst::First);
            }
            AstNode::Symbol(Op::Rest) => {
                if args.is_empty() { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.emit(Inst::Rest);
            }
            AstNode::Symbol(Op::Get) => {
                if args.len() < 2 { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]); // record
                self.compile_node(&args[1]); // key
                self.emit(Inst::GetField);
            }
            AstNode::Symbol(Op::Plus) => {
                if args.len() < 2 { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.compile_node(&args[1]);
                self.emit(Inst::Add);
            }
            AstNode::Symbol(Op::Gt) => {
                if args.len() < 2 { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.compile_node(&args[1]);
                self.emit(Inst::Gt);
            }
            AstNode::Symbol(Op::Lt) => {
                if args.len() < 2 { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.compile_node(&args[1]);
                self.emit(Inst::Lt);
            }
            AstNode::Symbol(Op::Eq) => {
                if args.len() < 2 { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.compile_node(&args[1]);
                self.emit(Inst::Eq);
            }
            AstNode::Symbol(Op::Not) => {
                if args.is_empty() { self.emit(Inst::PushNil); return; }
                self.compile_node(&args[0]);
                self.emit(Inst::Not);
            }
            // Unsupported ops: compile args for error propagation, then discard.
            // In Python, _eval_list evaluates all args before checking the op name,
            // so exceptions from arg evaluation propagate even for unknown ops.
            _ => {
                if args.is_empty() {
                    self.emit(Inst::PushNil);
                } else {
                    let n = args.len().min(255);
                    for arg in &args[..n] {
                        self.compile_node(arg);
                    }
                    self.emit(Inst::DiscardArgs(n as u8));
                }
            }
        }
    }

    /// Compile standalone (fn [x] body).
    /// In Python this creates a closure, which is a truthy callable.
    /// We can't create a real callable in the VM, but we push a truthy
    /// sentinel so that truthiness checks (and, or, not, filter body, if)
    /// behave the same as Python. We use Str("<closure>") because:
    /// - It's truthy (like a Python closure)
    /// - partial_credit treats it as type-mismatch (0.05), matching Python's
    ///   behavior for closures compared against int/list/dict targets
    fn compile_fn(&mut self, _args: &[AstNode]) {
        let idx = self.intern_string("<closure>");
        self.emit(Inst::PushStr(idx));
    }

    fn compile_if(&mut self, args: &[AstNode]) {
        if args.is_empty() {
            self.emit(Inst::PushNil);
            return;
        }
        // Compile condition
        self.compile_node(&args[0]);
        let jump_false = self.emit(Inst::JumpIfFalse(0)); // placeholder

        // Then branch
        if args.len() > 1 {
            self.compile_node(&args[1]);
        } else {
            self.emit(Inst::PushNil);
        }
        let jump_end = self.emit(Inst::Jump(0)); // placeholder

        // Else branch
        let else_ip = self.instructions.len() as u16;
        self.instructions[jump_false] = Inst::JumpIfFalse(else_ip);
        if args.len() > 2 {
            self.compile_node(&args[2]);
        } else {
            self.emit(Inst::PushNil);
        }

        let end_ip = self.instructions.len() as u16;
        self.instructions[jump_end] = Inst::Jump(end_ip);
    }

    fn compile_and(&mut self, args: &[AstNode]) {
        if args.len() < 2 {
            self.emit(Inst::PushNil);
            return;
        }
        self.compile_node(&args[0]);
        let jump_false = self.emit(Inst::JumpIfFalse(0)); // placeholder
        self.compile_node(&args[1]);
        let jump_end = self.emit(Inst::Jump(0)); // placeholder

        let false_ip = self.instructions.len() as u16;
        self.instructions[jump_false] = Inst::JumpIfFalse(false_ip);
        // Push the falsy value from first arg
        self.compile_node(&args[0]);

        let end_ip = self.instructions.len() as u16;
        self.instructions[jump_end] = Inst::Jump(end_ip);
    }

    fn compile_or(&mut self, args: &[AstNode]) {
        if args.len() < 2 {
            self.emit(Inst::PushNil);
            return;
        }
        self.compile_node(&args[0]);
        // If truthy, we want the first value. If falsy, evaluate second.
        // JumpIfFalse -> evaluate second arg
        let jump_false = self.emit(Inst::JumpIfFalse(0));
        // First was truthy — re-evaluate to get value on stack
        self.compile_node(&args[0]);
        let jump_end = self.emit(Inst::Jump(0));

        let false_ip = self.instructions.len() as u16;
        self.instructions[jump_false] = Inst::JumpIfFalse(false_ip);
        self.compile_node(&args[1]);

        let end_ip = self.instructions.len() as u16;
        self.instructions[jump_end] = Inst::Jump(end_ip);
    }

    fn compile_filter(&mut self, args: &[AstNode]) {
        // (filter fn_expr data_expr)
        if args.len() < 2 {
            self.emit(Inst::PushNil);
            return;
        }

        // Extract param name and body from the fn expression
        let (param_name, body) = match &args[0] {
            AstNode::ListExpr(fn_items) if fn_items.len() >= 3 => {
                match &fn_items[0] {
                    AstNode::Symbol(Op::Fn) => {
                        let param = match &fn_items[1] {
                            AstNode::SymbolStr(s) => s.clone(),
                            AstNode::Symbol(op) => op.to_str().to_string(),
                            _ => "x".to_string(),
                        };
                        (param, &fn_items[2])
                    }
                    _ => { self.emit(Inst::PushNil); return; }
                }
            }
            _ => { self.emit(Inst::PushNil); return; }
        };

        let param_slot = self.alloc_local();

        // Compile data expression (pushes list onto stack)
        self.compile_node(&args[1]);

        // Emit FilterBegin with placeholder end_ip
        let begin_idx = self.emit(Inst::FilterBegin(param_slot, 0));

        // Compile closure body in new scope
        self.scopes.push(HashMap::from([(param_name, param_slot)]));
        self.compile_node(body);
        self.scopes.pop();

        self.emit(Inst::FilterEnd);

        // Patch end_ip
        let end_ip = self.instructions.len() as u16;
        self.instructions[begin_idx] = Inst::FilterBegin(param_slot, end_ip);
    }

    fn compile_map(&mut self, args: &[AstNode]) {
        // (map fn_expr data_expr)
        if args.len() < 2 {
            self.emit(Inst::PushNil);
            return;
        }

        let (param_name, body) = match &args[0] {
            AstNode::ListExpr(fn_items) if fn_items.len() >= 3 => {
                match &fn_items[0] {
                    AstNode::Symbol(Op::Fn) => {
                        let param = match &fn_items[1] {
                            AstNode::SymbolStr(s) => s.clone(),
                            AstNode::Symbol(op) => op.to_str().to_string(),
                            _ => "x".to_string(),
                        };
                        (param, &fn_items[2])
                    }
                    _ => { self.emit(Inst::PushNil); return; }
                }
            }
            _ => { self.emit(Inst::PushNil); return; }
        };

        let param_slot = self.alloc_local();

        self.compile_node(&args[1]);

        let begin_idx = self.emit(Inst::MapBegin(param_slot, 0));

        self.scopes.push(HashMap::from([(param_name, param_slot)]));
        self.compile_node(body);
        self.scopes.pop();

        self.emit(Inst::MapEnd);

        let end_ip = self.instructions.len() as u16;
        self.instructions[begin_idx] = Inst::MapBegin(param_slot, end_ip);
    }
}

/// Compile an AstNode into bytecode.
pub fn compile(ast: &AstNode, source: String, bond_count: usize) -> Bytecode {
    let mut compiler = Compiler::new();
    compiler.compile_node(ast);
    compiler.emit(Inst::Return);
    Bytecode {
        instructions: compiler.instructions,
        string_pool: compiler.string_pool,
        source,
        bond_count,
    }
}
