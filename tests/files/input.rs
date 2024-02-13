extern crate python_stdlib;
use python_stdlib::builtin::exit;
use std::process::ExitCode;
use python_stdlib::builtin::input;
fn main() -> ExitCode {
print!("{}*{}*{}\r\n", "Hello, World!", "Hello, Rust!", 8);
print!("{}?\n", 42);
let x = input("> ");
println!("{}", x);
return exit(0);
}
