from rusttranspiler.main import main
from os.path import join


def test_hello_world():
    with open(join("tests", "files", "hello_world.rs"), "r") as f:
        expected = f.read()

    with open(join("tests", "files", "hello_world.py"), "r") as input:
        lex, output = main(input)
    assert output == expected


def test_hello_world_kw():
    with open(join("tests", "files", "hello_world_kw.rs"), "r") as f:
        expected = f.read()

    with open(join("tests", "files", "hello_world_kw.py"), "r") as input:
        lex, output = main(input)

    assert output == expected
