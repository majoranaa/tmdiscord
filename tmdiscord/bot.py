from tmdiscord import config as bot_config


class TerraformingMarsDiscordBot:
    def __init__(self, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.config = config

    def run(self):
        print(f"delay_length: {self.config.delay_length}")
