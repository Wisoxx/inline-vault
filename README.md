# Inline Vault Bot

[![Telegram](https://img.shields.io/badge/Telegram-Inline_Vault_Bot-blue)](https://t.me/inlinevaultbot)

**Inline Vault Bot** is a personal storage assistant for Telegram that allows users to save and retrieve various types of media and text efficiently through inline queries. The bot organizes content based on user-provided descriptions and provides quick access through search functionality.

## Features

- 📁 **Store Various Media**: Save photos, videos, GIFs, stickers, audio, voice messages, and documents.
- 🔎 **Fast Retrieval**: Use inline queries to quickly find and send stored media.
- 🏷 **Description-Based Search**: Organize and find content using text-based descriptions.
- 🛠 **Inline Mode**: Search and share media directly in any chat without opening the bot.
- 🌍 **Multi-language Support**: Interface available in English, Ukrainian, and Polish.
- ❌ **Delete Stored Content**: Remove items from the storage when needed.
- 📌 **Persistent Storage**: Saves data in a structured database for long-term access.

## Installation

This bot is hosted on **PythonAnywhere** and built with **Flask** and **Telepot**.
To set up a local development environment:

```sh
# Clone the repository
git clone https://github.com/Wisoxx/inline-vault.git
cd words-reminder

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Set up Telegram bot**
   - Create a bot via [BotFather](https://t.me/BotFather) and obtain the API token.
2. **Set environment variables**
   - Create a `.env` file with the following:
     ```env
     TELEGRAM_TOKEN=your_telegram_bot_token
     SITE_URL=your_site_url
     SECRET=your_webhook_secret
     ```

## Usage

Start a conversation with the bot: [@inlinevaultbot](https://t.me/inlinevaultbot)

### Commands

- `/start` – Begin interaction and setup.
- `/help` – Show instructions.
- `/description` – Send the description assigned to next media.
- `/delete` – Enter deletion mode to remove stored media.
- `/cancel` – Exit the current action mode.
- `/done` – Complete deleting items.

## Inline Query System

The bot allows users to search for and send saved media using inline mode:

1. Type `@inline_vault_bot <query>` in any chat. 
2. The bot will return matching results based on stored descriptions. 
3. Select the desired media to send it instantly.

## Database Structure

The bot uses **SQLite** with the following tables:

- **Users**: Stores user preferences.
- **Media**: Stores saved files with descriptions, captions, and media types.
- **Temp**: Temporary storage for ongoing user actions.

## Logging

- Logs are stored in `logs/app.log` using **RotatingFileHandler**.
- Flask provides an endpoint to view logs in a web browser at the `{SITE_URL}/{SECRET}/remind_all` endpoint.

## Deployment

1. **Set up on PythonAnywhere**
   - Create an account
   - Create and configure a **Flask web app**. For a detailed guide, refer to [Building a simple Telegram bot using PythonAnywhere](https://blog.pythonanywhere.com/148/).
   - Change WSGI file configuration to:
   ```python
   # This file contains the WSGI configuration required to serve up your
   # web application at http://<your-username>.pythonanywhere.com/
   # It works by setting the variable 'application' to a WSGI handler of some
   # description.
   
   import sys
   import os
   from dotenv import load_dotenv
   
   # add your project directory to the sys.path
   project_home = '/home/YOUR-USERNAME/mysite'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path
   
   project_folder = os.path.expanduser('~/mysite')
   load_dotenv(os.path.join(project_folder, '.env'))
   
   # import flask app but need to call it "application" for WSGI to work
   from flask_app import app as application  # noqa
   ```
   - Run commands mentioned in **Installation** in `/mysite` folder (`cd /mysite` first).

## Contributing

Feel free to submit issues or create pull requests. Contributions are welcome!

## License

MIT License © 2025 Bohdan Tavanov
