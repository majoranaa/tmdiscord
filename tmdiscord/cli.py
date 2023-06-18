import jsonargparse
from tmdiscord import bot
from tmdiscord import config as bot_config


def run():
    config = jsonargparse.CLI(
        bot_config.TerraformingMarsDiscordBotConfig,
        as_positional=False,
        exit_on_error=False,
        prog="tmdiscord",
    )
    bot.TerraformingMarsDiscordBot().run(config)
