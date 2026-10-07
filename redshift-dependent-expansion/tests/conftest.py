"""Keep the public tree clean while tests run: never write bytecode."""

import sys

sys.dont_write_bytecode = True
