# Nazh | Asynchronous Python Automation & Dice Engine

Nazh is a stateful Python application designed to handle high-concurrency dice-rolling requests for tabletop gaming via the Discord API. Built with a focus on service reliability and asynchronous performance, the project serves as a demonstration of production-ready automation and modular system architecture.

## 🛠 Infrastructure & Reliability Features
To ensure 24/7 service availability in a cloud-native environment, Nazh implements several "Infrastructure-as-Software" patterns:
- Sidecar Heartbeat Service: Implements a Flask-based web server running on a background daemon thread to provide a health-check endpoint for cloud platform monitors (e.g., Render).
- Asynchronous Event Loop: Utilizes asyncio and discord.py to manage non-blocking I/O operations, allowing the bot to scale across multiple concurrent requests without process blocking.
- Secure Configuration Management: Employs python-dotenv for externalized secret management, ensuring sensitive API credentials remain isolated from the application logic.
- Telemetry & Observability: Includes automated initialization logging to track service load (Guild counts) and system readiness upon deployment.

## 🏗 Modular Architecture
The codebase is organized into discrete modules to ensure maintainability and testability:
- main.py: The central orchestrator that manages the bot lifecycle and event listeners.
- dice_roll.py: A dedicated engine utilizing Python's secrets module for cryptographically secure randomization.
- dice_views.py: A complex UI state manager that handles ephemeral interactions and transient data storage during the "Build" process.
- web_server.py: The uptime-persistence layer that prevents platform-enforced idling.

## 🚀 Deployment & Local Setup
### Prerequisites
- Python 3.8+
- A Discord Bot Token (via Discord Developer Portal)

### Installation
1. Clone the repository:
```
git clone https://github.com/NevinsN/Nazh.git
```
2. Install dependencies:
```  
pip install -r requirements.txt
```
3. Configure Environment Variables: Create a .env file in the root directory:
```
DISCORD_TOKEN=your_token_here
```
4. Run the Service:
```
python main.py
```

## 📈 SRE Insights
By hosting this on Render and utilizing the keep_alive threading logic, this project maintains high uptime despite being hosted on a platform with aggressive idling policies. This demonstrates the ability to solve operational constraints through creative software engineering
