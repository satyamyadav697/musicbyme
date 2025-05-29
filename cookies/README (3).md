
# 🐳 Docker Deployment Guide — DeadlineTech Bot

## 📦 Prerequisites

Before you begin, ensure you have:

- [Docker](https://www.docker.com/products/docker-desktop) installed (version 20+ recommended)
- A `start` script in your root directory (make sure it's executable: `chmod +x start`)
- A `requirements.txt` file for Python dependencies
- Source code inside the same directory as your Dockerfile

---

## 🛠 Dockerfile Summary

This project uses:

- **Python 3.10**
- **Node.js v18 (via NVM)**
- **FFmpeg** for media handling

---

## 🚀 Steps to Build & Run

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/deadlinetech-bot.git
cd deadlinetech-bot
```

### 2. Build the Docker Image

```bash
docker build -t deadlinetech-bot .
```

> This step may take several minutes the first time.

### 3. Run the Container

```bash
docker run -it --restart unless-stopped --name dt-bot deadlinetech-bot
```

This will:
- Run the bot inside a container
- Automatically restart on crash or reboot

### Optional: Run Detached

```bash
docker run -dit --restart unless-stopped --name dt-bot deadlinetech-bot
```

---

## ⚙ Environment Variables

If your app uses environment variables (like API keys or tokens), you can provide them like this:

```bash
docker run -it \
  -e API_ID=123456 \
  -e API_HASH=abcdef1234567890 \
  -e BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 \
  --name dt-bot \
  deadlinetech-bot
```

You can also create a `.env` file and load it with:

```bash
docker run --env-file .env -it --name dt-bot deadlinetech-bot
```

---

## 📄 File Structure Example

```
📁 deadlinetech-bot/
├── Dockerfile
├── requirements.txt
├── start
├── config.py
├── main.py
└── DeadlineTech/
    └── ...
```

---

## 📌 Common Commands

- **Stop the container**  
  `docker stop dt-bot`

- **Start it again**  
  `docker start dt-bot`

- **View logs**  
  `docker logs -f dt-bot`

- **Rebuild after changes**  
  ```bash
  docker stop dt-bot && docker rm dt-bot
  docker build -t deadlinetech-bot .
  docker run -it --name dt-bot deadlinetech-bot
  ```

---

## ❓Troubleshooting

- **Permission denied on `start` script?**  
  Run: `chmod +x start`

- **NVM not loading properly?**  
  Make sure `start` runs under `bash` and `.bashrc` sources NVM

- **Not leaving chats / background jobs not running?**  
  Ensure `asyncio.create_task(...)` is included **after** app starts in your `init()` function.
