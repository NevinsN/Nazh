# Nazh Engine | Production-Grade Discord Utility
A high-concurrency, cryptographically secure dice engine built with SRE principles.

## 🏗 System Architecture
Unlike standard hobbyist bots, the Nazh Engine is built as a modular monolith with a sidecar observability pattern. This ensures that application logic, infrastructure configuration, and system monitoring remain decoupled.  

Key Components:
- **The Orchestrator (main.py):** A lightweight entry point that manages the application lifecycle and graceful shutdowns.
- **The Core (modules/bot.py):** An encapsulated Bot class that utilizes Cogs for modular command loading.
- **The Engine (modules/dice_roll.py):** Uses secrets.randbelow() for cryptographically secure randomization (CSPRNG), ensuring fairness for tabletop gaming.
- **The Dashboard (web_server.py):** A Flask-based “Sidecar” service that provides real-time telemetry and prevents platform idling.
 
## 🛠 SRE & Reliability Features
This project serves as a demonstration of Operational Maturity:
1. **Fail-Fast Configuration:** Implements a validated Config dataclass. If environment variables (Secrets) are missing or malformed, the system terminates during the boot sequence to prevent “zombie” processes.
2. **Structured Observability:** Replaces standard print statements with a professional logging pipeline (logging.RotatingFileHandler). Logs include timestamps, module origins, and severity levels for easy ingestion into ELK or Grafana.
3. **Backoff & Retry Logic:** Handles Discord API rate limits (HTTP 429) using an exponential backoff strategy, preventing IP bans during high-traffic reconnects.
4. **Health-Check Sidecar:** A dedicated web endpoint provides a “Heartbeat” for cloud monitors (Render/AWS), exposing live metrics like latency and guild connectivity.
 
## 🚀 Deployment & Monitoring
The bot is designed for containerized deployment (Docker/Render).
### Live Telemetry
The integrated SRE Dashboard can be accessed at the root URL of the deployment, providing real-time insights into:
- **Bot Latency:** Real-time WebSocket ping.
- **Process Uptime:** Tracking system stability.
- **Version Traceability:** Reporting the specific Git commit hash currently live in production.
 
## 💻 Tech Stack
- **Language:** Python 3.10+ (Asynchronous I/O)
- **Frameworks:** Discord.py, Flask
- **Security:** python-dotenv, secrets (CSPRNG)
- **Observability: Python Logging, Flask Telemetry
