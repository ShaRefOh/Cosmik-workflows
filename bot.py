import os
import discord
from discord import app_commands
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class StandupBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        @self.tree.command(name="standup", description="Submit an update")
        @app_commands.describe(text="Your update")
        async def standup(interaction: discord.Interaction, text: str):
            await interaction.response.defer()
            create_notion_entry(interaction.user, text)
            await interaction.followup.send(
                f"{interaction.user.mention} posted an update: {text}"
            )

        await self.tree.sync()

def create_notion_entry(user: discord.abc.User, text: str) -> None:
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": f"updates by {user.name}"}}]},
            "Notes & Updates": {
                "rich_text": [{"text": {"content": text}}]
            },
        },
    }
    requests.post(url, headers=headers, json=data)

def main() -> None:
    bot = StandupBot()
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
