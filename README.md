# Cosmik-workflows

This repo contains a simple Discord bot that forwards `/standup` updates to a Notion database. It is ready to deploy on [Render](https://render.com).

## Deployment

1. Set the environment variables `DISCORD_TOKEN`, `NOTION_TOKEN`, and `NOTION_DATABASE_ID` in your Render service.
2. Deploy using the provided `Procfile` which runs `python bot.py`.

The bot registers a `/standup` slash command. When invoked, it displays a modal asking for the following fields:

- **In Progress Today** – work in progress today
- **Planned Next** – what you will do next
- **Notes & Updates** – any notes or updates
- **Availability** – your availability today

After submitting, the responses are saved to Notion and echoed back to the channel.
