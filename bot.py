import os
import re
import json
import discord
from discord import app_commands
from discord.ui import TextInput, Modal
import requests

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

try:
    with open("forum_channels.json", "r") as f:
        FORUM_CHANNEL_IDS = json.load(f)
except Exception:
    FORUM_CHANNEL_IDS = []

class StandupBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        @self.tree.command(name="standup", description="Submit an update")
        async def standup(interaction: discord.Interaction):
            modal = StandupModal(interaction.user)
            await interaction.response.send_modal(modal)

        await self.tree.sync()

    async def on_thread_create(self, thread: discord.Thread) -> None:
        if (
            isinstance(thread.parent, discord.ForumChannel)
            and thread.parent.id in FORUM_CHANNEL_IDS
        ):
            try:
                message = await thread.fetch_message(thread.id)
            except Exception:
                return
            first_url_match = re.search(r"https?://\S+", message.content)
            first_url = first_url_match.group(0) if first_url_match else ""
            create_forum_notion_entry(
                thread.name,
                message.author,
                first_url,
                message.content,
            )

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

def create_forum_notion_entry(
    post_name: str,
    author: discord.abc.User,
    url_link: str,
    notes: str,
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
            "Name": {
                "title": [
                    {"text": {"content": f"{post_name} by {author.name}"}}
                ]
            },
            "URL": {"url": url_link if url_link else None},
            "Notes": {"rich_text": [{"text": {"content": notes}}]},
        },
    }
    requests.post(url, headers=headers, json=data)

def main() -> None:
    bot = StandupBot()
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
