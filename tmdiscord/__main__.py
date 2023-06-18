from tmdiscord import bot

import sys

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

try:
    bot.run()
    sys.exit(EXIT_SUCCESS)
except Exception as e:
    msg = str(e)
    log_msg = f": {msg}" if msg else ""
    # TODO: use logger
    print(
        f"Encountered exception [{type(e).__name__}{log_msg}]. "
        f"Exiting with code [{EXIT_FAILURE}]."
    )
    sys.exit(EXIT_FAILURE)
