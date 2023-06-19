import requests

from tmdiscord import config as bot_config


class TerraformingMarsDiscordBot:
    def __init__(self, config: bot_config.TerraformingMarsDiscordBotConfig):
        self.config = config
        print(f"webhook url: {self.config.webhook_url}")

    def run(self):
        r = requests.post(self.config.webhook_url, json={"content": "hello"})
        r.raise_for_status()
