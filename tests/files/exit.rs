extern crate python_stdlib;
use python_stdlib::builtin::exit;
use std::process::ExitCode;
fn main() -> ExitCode {
print!("{}\r\n", "Hello, World!");
return exit(1);
}
