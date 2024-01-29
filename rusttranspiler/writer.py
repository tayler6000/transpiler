from rusttranspiler.lex import Instruction


TYPE_MAP = {
    "int": "int",
    "str": "String",
    "None": "()",
    None: "()",
}


def trans(_type: str) -> str:
    return TYPE_MAP.get(_type, _type)


def write(tokens: list[Instruction], output: str) -> None:
    with open(output, "w") as file:
        for x in tokens:
            if x.opname == "CALL":
                # context = x.args["context"]
                func = x.args["func"]
                args = x.args["args"]
                if func == "print":
                    line = call_print(x)
                    file.write(line + "\n")
                    continue
                line = func + "("
                argline = ""
                for arg in args:
                    argline += f'"{arg}", '
                line += argline[0:-2] + ");"
            elif x.opname == "RETURN_VALUE":
                line = f"return {trans(x.args['value'])};"
            elif x.opname == "START_FUNCTION":
                fn_name = x.args["name"]
                return_type = TYPE_MAP["None"]
                line = f"fn {fn_name}("
                if x.args["args"] is not None:
                    args = x.args["args"]
                    i = 0
                    while i < len(args):
                        if args[i] == "return":
                            return_type = trans(args[i + 1])
                            i += 2
                            continue
                        _type = trans(args[i + 1])
                        line += f"{args[i]}: {_type}"
                        i += 2
                line += f") -> {return_type} " + "{"
            elif x.opname == "END_SCOPE":
                line = "}"
            file.write(line + "\n")


def call_print(x: Instruction) -> str:
    func = x.args["func"]
    args = x.args["args"]
    if func == "print":
        func = "println!"
    line = func + '('
    if len(args) > 1 or type(args[0]) is not str:
        line += '"' + ("{} " * len(args))[0:-1] + '", '
    argline = ""
    for arg in args:
        if type(arg) is str:
            argline += f'"{arg}", '
        else:
            argline += f'{arg}, '
    line += argline[0:-2] + ");"
    return line
