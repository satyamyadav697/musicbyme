<details>
<summary><b>📛 Docker Deployment Guide</b></summary>


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
git clone https://github.com/DeadlineTech/music.git
cd music
```

### 2. Build the Docker Image

```bash
docker build -t music .
```

> This step may take several minutes the first time.

### 3. Run the Container

```bash
docker run -it --restart unless-stopped --name dt-bot music
```

This will:
- Run the bot inside a container
- Automatically restart on crash or reboot

### Optional: Run Detached

```bash
docker run -dit --restart unless-stopped --name dt-bot music
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
  docker build -t music .
  docker run -it --name dt-bot music
  ```
</details>
