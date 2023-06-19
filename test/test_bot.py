from tmdiscord import bot
from tmdiscord import config as bot_config


def test_bot():
    config = bot_config.TerraformingMarsDiscordBotConfig()
    bot.TerraformingMarsDiscordBot(config).run()
    assert True
