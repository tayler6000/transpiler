from dataclasses import dataclass
from typing import Any, NamedTuple
import dis


class LexError(Exception):
    pass


@dataclass
class Instruction:
    opname: str
    args: dict[str, Any]


class Name(NamedTuple):
    value: str

    def __repr__(self) -> str:
        return self.value


class Kwarg(NamedTuple):
    key: str
    val: Any


class StdLib(NamedTuple):
    lib: str


END_SCOPE: None | int = None
FUNC: None | Instruction = None
NAMES: dict[str, Any] = {}


def lex(src: list[str], t: dis.Bytecode) -> list[Instruction]:
    global END_SCOPE
    global FUNC
    stack: list[Any] = []
    lexed: list[Instruction] = [
        Instruction(
            opname="IMPORT_CRATE",
            args={"import": "python_stdlib"},
        ),
    ]
    tokens = list(t)
    while len(tokens) >= 1:
        x = tokens.pop(0)
        if END_SCOPE is not None:
            if END_SCOPE == x.offset:
                lexed.append(Instruction(opname="END_SCOPE", args={}))
                END_SCOPE = None
                FUNC = None
        match x.opname:
            case "RESUME":
                continue  # NOOP
            case "KW_NAMES":
                kw_names(src, x, tokens, stack, lexed)
            case "CALL_FUNCTION_KW":
                call_function_kw(x, tokens, stack, lexed)
            case "LOAD_NAME":
                load_name(x, tokens, stack, lexed)
            case "IMPORT_NAME":
                import_name(x, tokens, stack, lexed)
            case "LOAD_CONST":
                if type(x.argval) is str:
                    stack.append(repr(x.argval).strip("'"))
                    continue
                stack.append(x.argval)
            case "PUSH_NULL":
                stack.append(None)
            case "CALL":
                call(x, tokens, stack, lexed)
            case "RETURN_VALUE":
                if END_SCOPE is None:
                    stack.pop()
                    continue
                lexed.append(
                    Instruction(
                        opname="RETURN_VALUE", args={"value": stack.pop()}
                    )
                )
            case "RETURN_CONST":
                if END_SCOPE is None:
                    continue
                if FUNC is not None:
                    if "return" in FUNC.args["args"]:
                        return_type = FUNC.args["args"][
                            FUNC.args["args"].index("return") + 1
                        ]
                        if return_type == "ExitCode" and x.argval is None:
                            continue
                        # TODO: check if return type does not match the return
                        # statment and error.
                lexed.append(
                    Instruction(
                        opname="RETURN_VALUE", args={"value": x.argval}
                    )
                )
            case _:
                raise LexError(f"Unhandled Bytecode Instruction: {x}")

    return lexed


def kw_names(
    src: list[str],
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    assert type(x.argval) is tuple
    istack: list[Any] = []
    kwargs = x.argval
    for _ in range(len(kwargs)):
        istack.append(stack.pop())
    istack.reverse()
    for arg, val in zip(kwargs, istack):
        stack.append(Kwarg(key=arg, val=val))


def load_name(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    global END_SCOPE
    global FUNC
    inst1 = tokens.pop(0)
    inst2 = tokens.pop(0)
    inst3 = tokens.pop(0)
    if (
        x.argval == "__name__"
        and inst1.opname == "LOAD_CONST"
        and inst1.argval == "__main__"
        and inst2.opname == "COMPARE_OP"
        and inst2.argval == "=="
        and inst3.opname == "POP_JUMP_IF_FALSE"
    ):
        END_SCOPE = inst3.argval
        FUNC = Instruction(
            opname="START_FUNCTION",
            args={"name": "main", "args": tuple()},
        )
        lexed.append(FUNC)
    else:
        tokens.insert(0, inst3)
        tokens.insert(0, inst2)
        tokens.insert(0, inst1)
        stack.append(Name(x.argval))
        global NAMES
        if NAMES.get(x.argval) == StdLib("sys"):
            inst = tokens.pop(0)
            if inst.opname == "LOAD_ATTR":
                if inst.argval == "exit":
                    x = inst
                    stack.pop()
                    stack.append(Name(inst.argval))
                else:
                    tokens.insert(0, inst)
        if x.argval == "exit":
            for instruction in lexed:
                if (
                    instruction.opname == "START_FUNCTION"
                    and instruction.args["name"] == "main"
                ):
                    args = instruction.args["args"]
                    if "return" not in args:
                        instruction.args["args"] = args + (
                            "return",
                            "ExitCode",
                        )
            lexed.insert(
                1,
                Instruction(
                    opname="IMPORT_RUST",
                    args={"import": "std::process::ExitCode"},
                ),
            )
            lexed.insert(
                1,
                Instruction(
                    opname="IMPORT_RUST",
                    args={"import": "python_stdlib::builtin::exit"},
                ),
            )


def import_name(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    SUPPORTED_STDLIB = {"sys"}
    stack.pop()  # fromlist
    level = stack.pop()
    if level != 0:
        raise LexError("Relative imports not supported, yet")
    if x.argval not in SUPPORTED_STDLIB:
        raise LexError(f"Not able to import from {x.argval}, yet")
    inst = tokens.pop(0)
    if not inst.opname == "STORE_NAME":
        stack.append(StdLib(x.argval))
        return
    global NAMES
    NAMES[inst.argval] = StdLib(x.argval)


def call_function_kw(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    kwargs = stack.pop()
    istack: list[Any] = []
    for _ in range(len(kwargs)):
        istack.append(stack.pop())
    istack.reverse()
    for key, val in zip(kwargs, istack):
        stack.append(Kwarg(key=key, val=val))
    call(x, tokens, stack, lexed)


def call(
    x: dis.Instruction,
    tokens: list[dis.Instruction],
    stack: list[Any],
    lexed: list[Instruction],
) -> None:
    argc = x.argval
    arguments: list[Any] = []
    for _ in range(argc):
        arguments.append(stack.pop())
    arguments.reverse()
    kwargs: dict[str, Any] = {}
    to_pop: list[Kwarg] = []
    for argument in arguments:
        if type(argument) is Kwarg:
            to_pop.append(argument)
    for argument in to_pop:
        kwargs[argument.key] = argument.val
        arguments.pop(arguments.index(argument))
    stack1 = stack.pop()
    stack2 = stack.pop()
    if stack2 is None:
        func = stack1.value
        _self = None
    else:
        func = stack2.value
        _self = stack1
    inst1 = tokens.pop(0)
    match func:
        case "exit":
            exit_code = arguments[0] if arguments else 0
            lexed.append(
                Instruction(
                    opname="RETURN_VALUE", args={"value": f"exit({exit_code})"}
                )
            )
            return
        case "input":
            lexed.insert(
                1,
                Instruction(
                    opname="IMPORT_RUST",
                    args={"import": "python_stdlib::builtin::input"},
                ),
            )
    if inst1.opname == "POP_TOP":
        lexed.append(
            Instruction(
                opname="CALL",
                args={
                    "context": _self,
                    "func": func,
                    "args": arguments,
                    "kwargs": kwargs,
                },
            )
        )
    elif inst1.opname == "STORE_NAME":
        lexed.append(Instruction(opname="STORE", args={"var": inst1.argval}))
        lexed.append(
            Instruction(
                opname="CALL",
                args={
                    "context": _self,
                    "func": func,
                    "args": arguments,
                },
            )
        )
    else:
        tokens.insert(0, inst1)
