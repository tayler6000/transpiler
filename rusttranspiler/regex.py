import re

KW_FIND = re.compile(r"""(?P<arg>\w+)\s*?=\s*?["']?(?P<val>.+?)["']?[\w,)]""")
