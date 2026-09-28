# Telegram Video Cover Bot

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.31.0-2CA5E0)](https://github.com/aiogram/aiogram)
[![aiosqlite](https://img.shields.io/badge/aiosqlite-0.22.1-003B57)](https://github.com/omnilib/aiosqlite)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A simple Telegram bot that lets you change a video's cover by sending a video followed by an image.

This repository is intentionally kept simple and is designed for **personal use, learning, testing, and small self-hosted deployments**.

## ✨ How it works

1. Send a video to the bot.
2. Send the image you want to use as the video's cover.
3. The bot sends the video back with the new cover.

The bot keeps the video's caption and caption formatting when sending it back.

## ⚠️ Simple Version

This is the **simple version** of the bot.

It uses:

* Python
* aiogram
* SQLite
* aiosqlite
* Long polling

There is no Redis, external database, worker system, or other infrastructure required.

This version is mainly intended for:

* Personal use
* Learning
* Testing
* Small self-hosted bots
* People who want something easy to run

### Public Usage & Rate Limits

This version does **not** include advanced rate limiting, flood protection, or a processing queue.

If you deploy this bot publicly, users can send many videos at the same time. A large number of requests may cause high load or result in Telegram API rate limits.

For larger public deployments, use the advanced version instead:

**Advanced version:** [Telegram Video Cover Bot — Advanced](https://github.com/BigDaddyAman/Video-Cover-Telegram-Bot)

The advanced version is designed with a more scalable architecture and can use Redis and background workers.

## 🧪 Try the Bot

You can test a deployed version before setting up your own bot:

**Test Bot:** [@VideoCoverToolBot](https://t.me/VideoCoverToolBot)

## 🚀 Run Locally

### Requirements

* Python 3.13 recommended
* A Telegram bot token

Create a bot using [@BotFather](https://t.me/BotFather) and get your bot token.

### 1. Clone the repository

```bash
git clone https://github.com/BigDaddyAman/telegram-video-cover-bot.git
cd telegram-video-cover-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the bot

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

On Windows, you can simply copy the file manually or run:

```powershell
Copy-Item .env.example .env
```

Open `.env` and add your bot token:

```env
BOT_TOKEN=your_bot_token_here
```

### 4. Start the bot

```bash
python main.py
```

You should see the bot start in your terminal.

Press `Ctrl+C` to stop it.

## 🐳 Run with Docker

You can also run the bot using Docker.

### Build the image

```bash
docker build -t video-cover-bot .
```

### Run the container

```bash
docker run -d \
  --name video-cover-bot \
  --env-file .env \
  -v video-cover-data:/app \
  video-cover-bot
```

The Docker volume keeps the SQLite database persistent when the container is recreated.

To view the bot logs:

```bash
docker logs -f video-cover-bot
```

To stop the bot:

```bash
docker stop video-cover-bot
```

## 📁 Project Structure

```text
telegram-video-cover-bot/
├── .env.example
├── .gitignore
├── config.py
├── db.py
├── Dockerfile
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

The SQLite database (`bot.db`) is created automatically when the bot starts.

It is excluded from Git using `.gitignore`.

## 📦 Dependencies

The project uses pinned dependency versions:

```text
aiogram==3.31.0
aiosqlite==0.22.1
python-dotenv==1.2.3
```

Pinning the versions helps keep the environment consistent with the version tested for this project.

## 🔒 Environment Variables

Only one environment variable is required:

```env
BOT_TOKEN=your_bot_token_here
```

Never commit your `.env` file or expose your bot token publicly.

## 📄 License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
