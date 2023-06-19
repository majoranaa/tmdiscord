import jsonargparse
from tmdiscord import bot
from tmdiscord import config as bot_config


def parse_args():
    return jsonargparse.CLI(
        bot_config.TerraformingMarsDiscordBotConfig,
        as_positional=False,
        exit_on_error=False,
        prog="tmdiscord",
    )


def run():
    parser = jsonargparse.capture_parser(parse_args)
    try:
        config = parse_args()
        bot.TerraformingMarsDiscordBot(config).run()
    except jsonargparse.ArgumentError as e:
        print(e)
        print()
        print(parser.format_help())
        raise
