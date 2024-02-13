pub mod builtin {
    use std::io;
    use std::io::Write;
    use std::process::ExitCode;

    pub fn exit(code: u8) -> ExitCode {
        ExitCode::from(code)
    }

    pub fn input(prompt: &str) -> String {
        print!("{}", prompt);
        let _ = io::stdout().flush();
        let mut buff = String::new();
        let _ = io::stdin().read_line(&mut buff);
        let ret = buff.trim_end();
        String::from(ret)
    }
}

#[cfg(test)]
mod tests {
    use super::builtin::*;

    #[test]
    fn exit_codes() {
        let mut result = exit(0);
        let mut f = format!("{:?}", result);
        assert_eq!(f, String::from("ExitCode(ExitCode(0))"));
        result = exit(1);
        f = format!("{:?}", result);
        assert_eq!(f, String::from("ExitCode(ExitCode(1))"));
    }
}
