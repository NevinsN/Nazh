from flask import Flask
from threading import Thread

app = Flask(__name__)
# We will store a reference to the bot here
bot_reference = None

@app.route('/')
def home():
    return "Nahz Engine is Online."

@app.route('/guilds')
def list_guilds():
    if not bot_reference:
        return "Bot not yet initialized."
    
    # Creates a clean list of names and IDs for the browser
    guild_list = [f"{g.name} (ID: {g.id})" for g in bot_reference.guilds]
    return "<br>".join(guild_list) if guild_list else "No guilds joined yet."

def run_server():
    # Render uses port 8080 or the PORT env var
    app.run(host='0.0.0.0', port=8080)

def keep_alive(bot):
    global bot_reference
    bot_reference = bot # Connect the bot to the web server
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
