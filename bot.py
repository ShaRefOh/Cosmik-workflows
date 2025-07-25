import os
import discord
from discord import app_commands
from discord.ui import TextInput, Modal
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
        async def standup(interaction: discord.Interaction):
            modal = StandupModal(interaction.user)
            await interaction.response.send_modal(modal)

        await self.tree.sync()

class StandupModal(Modal):
    def __init__(self, user: discord.abc.User):
        super().__init__(title="Standup Update")
        self.user = user

        self.in_progress_today = TextInput(
            label="In Progress Today",
            placeholder="work in progress today",
            style=discord.TextStyle.paragraph,
            required=False,
        )

        self.planned_next = TextInput(
            label="Planned Next",
            placeholder="What I will do next",
            style=discord.TextStyle.paragraph,
            required=False,
        )

        self.notes_updates = TextInput(
            label="Notes & Updates",
            placeholder="Any notes or updates",
            style=discord.TextStyle.paragraph,
            required=False,
        )

        self.availability = TextInput(
            label="Availability",
            placeholder="What is my availability today",
            style=discord.TextStyle.short,
            required=False,
        )

        self.add_item(self.in_progress_today)
        self.add_item(self.planned_next)
        self.add_item(self.notes_updates)
        self.add_item(self.availability)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        create_notion_entry(
            self.user,
            self.in_progress_today.value,
            self.planned_next.value,
            self.notes_updates.value,
            self.availability.value,
        )
        await interaction.response.send_message(
            f"{self.user.mention} posted an update:\n"
            f"In Progress Today: {self.in_progress_today.value}\n"
            f"Planned Next: {self.planned_next.value}\n"
            f"Notes & Updates: {self.notes_updates.value}\n"
            f"Availability: {self.availability.value}"
        )

def create_notion_entry(
    user: discord.abc.User,
    in_progress_today: str,
    planned_next: str,
    notes_updates: str,
    availability: str,
) -> None:
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
            "In Progress Today": {
                "rich_text": [{"text": {"content": in_progress_today}}]
            },
            "Planned Next": {
                "rich_text": [{"text": {"content": planned_next}}]
            },
            "Notes & Updates": {
                "rich_text": [{"text": {"content": notes_updates}}]
            },
            "Availability": {
                "rich_text": [{"text": {"content": availability}}]
            },
        },
    }
    requests.post(url, headers=headers, json=data)

def main() -> None:
    bot = StandupBot()
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
