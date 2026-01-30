from flask import Flask
from threading import Thread
import os

app = Flask(__name__)
# Global reference to allow the web server to access the bot's live data
bot_instance = None

@app.route('/')
def home():
    """Standard health check endpoint."""
    return "Nahz Engine is Online."

@app.route('/guilds')
def list_guilds():
    """
    SRE Strategy: Move detailed guild logging to a private web endpoint
    to keep production logs clean (high signal-to-noise ratio).
    """
    if not bot_instance:
        return "Bot is still initializing. Please refresh in 30 seconds."
    
    # Builds a clean list of names and IDs for your browser
    guild_list = [f"<li><b>{g.name}</b> (ID: {g.id})</li>" for g in bot_instance.guilds]
    
    if not guild_list:
        return "The engine is online, but the bot is not currently in any guilds."
    
    return f"<h1>Active Guild Connectivity ({len(guild_list)})</h1><ul>" + "".join(guild_list) + "</ul>"

def run_server():
    # Render uses the PORT environment variable; default to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive(bot):
    """Starts the web server sidecar on a background daemon thread."""
    global bot_instance
    bot_instance = bot
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
