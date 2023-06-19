from tmdiscord import cli

import sys
import traceback

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE_ERROR = 2


try:
    cli.run()
    sys.exit(EXIT_SUCCESS)
except cli.UsageError:
    sys.exit(EXIT_USAGE_ERROR)
except Exception as e:
    # TODO: use logger
    print(f"Encountered internal error. Exiting with code [{EXIT_FAILURE}].")
    [print(line, end="") for line in traceback.format_exception(e)]
    sys.exit(EXIT_FAILURE)
