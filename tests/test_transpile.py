from rusttranspiler.main import main
import io


def test_hello_world():
    expected = (
        'fn main() -> () {\nprintln!("Hello, World!");\nreturn ();\n}\n'
    )
    input = io.BytesIO()
    input.write(b'if __name__ == "__main__":\n')
    input.write(b'    print("Hello, World!")\n')
    input.seek(0, 0)

    lex, output = main(io.TextIOWrapper(input))
    assert output == expected


def test_hello_world_kw():
    expected = (
        'fn main() -> () {\nprint!("{}*{}*{}?", "Hello, World!", '
        + '"Hello, Rust!", 8);\nprint!("{}!", 42);\nprint!("{}!",'
        + ' "Our transpiler now works");\nreturn ();\n}\n'
    )
    input = io.BytesIO()
    input.write(b'if __name__ == "__main__":\n    print("Hello, World!", ')
    input.write(b'"Hello, Rust!", 8, sep="*", end="?")\n    ')
    input.write(b'print(42, end="!")\n')
    input.write(b'    print("Our transpiler now works", end="!")\n')
    input.seek(0, 0)

    lex, output = main(io.TextIOWrapper(input))
    assert output == expected
