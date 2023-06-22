from tmdiscord import cli
import tmdiscord.logging
from tmdiscord.logging import logger

import sys


EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_USAGE_ERROR = 2


try:
    cli.run()
    sys.exit(EXIT_SUCCESS)
except cli.UsageError:
    sys.exit(EXIT_USAGE_ERROR)
except Exception:
    logger.opt(exception=True).error(
        "Encountered internal error. Exiting with code [{exit_code}].", exit_code=EXIT_FAILURE
    )
    if not tmdiscord.logging.is_configured():
        logger.critical(
            "Logger has not been configured. "
            "This means that not even CLI argument parsing completed."
        )
    sys.exit(EXIT_FAILURE)
