Nazh Engine | Production-Grade Discord Utility
A high-concurrency, cryptographically secure dice engine built with SRE principles.
🏗 System Architecture
Unlike standard hobbyist bots, the Nazh Engine is built as a modular monolith with a sidecar observability pattern. This ensures that application logic, infrastructure configuration, and system monitoring remain decoupled.
• The Orchestrator (main.py): A lightweight entry point that manages the application lifecycle and graceful shutdowns.
• The Core (modules/bot.py): An encapsulated Bot class that utilizes Cogs for modular command loading.
• The Engine (modules/dice_roll.py): Uses secrets.randbelow() for cryptographically secure randomization (CSPRNG), ensuring fairness for tabletop gaming.
• The Dashboard (web_server.py): A Flask-based “Sidecar” service that provides real-time telemetry and prevents platform idling.
🛠 SRE & Reliability Features
This project serves as a demonstration of Operational Maturity:
1. Fail-Fast Configuration: Implements a validated Config dataclass. If environment variables (Secrets) are missing or malformed, the system terminates during boot to prevent “zombie” processes.
2. Structured Observability: Replaces standard print statements with a professional logging pipeline (logging.RotatingFileHandler).
3. Compute Guardrails: Strict 20-dice-per-pool limit to prevent CPU exhaustion and ensure sub-200ms p99 latency.
4. CI/CD Health Checks: Integrated GitHub Actions run a unit test suite on every push to verify math and parsing integrity.
🚀 Installation & Setup
1. Prerequisites
• Python 3.11+
• A Discord Bot Token (via Discord Developer Portal)
2. Environment Configuration
Create a .env file in the root directory:
```
DISCORD_TOKEN=your_token_here
APP_ENV=production
```
3. Deployment
```
# Install dependencies
pip install -r requirements.txt

# Run the health check suite
python test_dice.py

# Launch the engine
python main.py
```
🎲 Game Mechanics & Usage
The Nazh Engine uses a unique Multi-Pool system, allowing up to 5 separate dice sets to be rolled in a single atomic transaction.
The /roll Command
• Skill Pools: Any pool containing a d20 is treated as a Skill Roll.
• Plot Die (add_plot): A specialized d6 with narrative triggers.
• Roll 1: +2 to d20 Total | Threat !!(T)
• Roll 2: +4 to d20 Total | Threat !!(T)
• Roll 5-6: Opportunity (O)
• Advantage/Disadvantage: Prefix pools with a or d (e.g., a1d20+5). Results show both dice, with arrows marking the kept value: [18↑(3)].
Interactive UI
• Add Plot Die Button: Appears only if a Plot Die isn’t already present.
• Copy Command Button: Opens a modal with the raw /roll string for quick rerolling on mobile.
🛠 Server Integration
To bring the Nazh Engine into a Discord guild:
1. Invite the Bot: Use the OAuth2 URL Generator in the Developer Portal.
2. Required Scopes: bot, applications.commands.
3. Permissions: Send Messages, Embed Links, Use External Emojis.
4. Command Sync: Commands are global. If they do not appear immediately, wait 60 minutes for Discord’s cache or trigger a manual sync.
💻 Tech Stack
• Language: Python 3.11+ (Asynchronous I/O)
• Frameworks: Discord.py, Flask
• Security: python-dotenv, secrets (CSPRNG)
• Observability: Python Logging, Flask Telemetry Dashboard
📊 Live Telemetry
The integrated SRE Dashboard (accessible at the root URL of your deployment) provides real-time insights into:
• Bot Latency: Real-time WebSocket ping.
• Success Rate: Tracking roll_success metrics.
• Version Traceability: Reporting the specific Git commit hash currently live in production.

🖋️ Project Origins & Methodology
The Nazh Engine is a collaborative engineering effort. The core logic, including the original dice-parsing engine and cryptographically secure randomization, was designed and authored by [Your Name/Username].
Development Workflow:
• Foundational Logic: The primary author provided the initial codebase and defined the modular “bucket” system for dice pools.
• AI-Assisted Scaling: Implementation was refined and scaled through iterative pair-programming with Gemini to integrate advanced SRE guardrails, asynchronous UI components, and automated CI/CD validation.
• Verification: All architectural decisions—from positional tagging to plot die interaction—were architected by the primary author to meet specific tabletop gaming requirements.
