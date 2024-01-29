from rusttranspiler.lex import Instruction


TYPE_MAP = {
    "int": "int",
    "str": "String",
    "None": "()",
    None: "()",
}


def trans(_type: str) -> str:
    return TYPE_MAP.get(_type, _type)


def translate(tokens: list[Instruction]) -> str:
    output = ""
    for x in tokens:
        if x.opname == "CALL":
            line = call(x)
        elif x.opname == "RETURN_VALUE":
            line = f"return {trans(x.args['value'])};"
        elif x.opname == "START_FUNCTION":
            line = start_function(x)
        elif x.opname == "END_SCOPE":
            line = "}"
        output += line + "\n"
    return output


def call(x: Instruction) -> str:
    # context = x.args["context"]
    func = x.args["func"]
    args = x.args["args"]
    if func == "print":
        line = call_print(x)
        return line
    line = func + "("
    argline = ""
    for arg in args:
        argline += f'"{arg}", '
    line += argline[0:-2] + ");"
    return line


def call_print(x: Instruction) -> str:
    func = x.args["func"]
    args = x.args["args"]
    sep = args["kwargs"].get("sep", " ")
    end = args["kwargs"].get("end", "\n")
    func = "println!"
    if end != "\n":
        func = "print!"
    line = func + "("
    if len(args) > 1 or type(args[0]) is not str:
        line += '"' + (("{}"+sep) * len(args))[0:-len(sep)]
        if end != "\n":
            line += end
        line += '", '
    argline = ""
    for arg in args:
        if type(arg) is str:
            argline += f'"{arg}", '
        else:
            argline += f"{arg}, "
    line += argline[0:-2] + ");"
    return line


def start_function(x: Instruction) -> str:
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
    return line
