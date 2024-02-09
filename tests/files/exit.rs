use std::process::ExitCode;
fn main() -> ExitCode {
print!("{}\r\n", "Hello, World!");
return ExitCode::from(1);
}
