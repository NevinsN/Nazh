from flask import Flask, render_template_string
from threading import Thread
import time

app = Flask(__name__)
# This will be set by the keep_alive function at boot
bot_instance = None
start_time = time.time()

# HTML Template with simple CSS for a "Dark Mode" SRE Dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Nazh Engine | Status</title>
    <style>
        body { font-family: sans-serif; background: #1a1a1a; color: #eee; padding: 20px; }
        .card { background: #2d2d2d; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 5px solid #7289da; }
        .stat { font-size: 24px; font-weight: bold; color: #fff; }
        .label { color: #888; font-size: 12px; text-transform: uppercase; }
        .status-up { color: #43b581; }
    </style>
</head>
<body>
    <h1>Nazh Engine <span class="status-up">● Online</span></h1>
    <div class="card">
        <div class="label">Bot Latency</div>
        <div class="stat">{{ latency }}ms</div>
    </div>
    <div class="card">
        <div class="label">Connected Guilds</div>
        <div class="stat">{{ guild_count }}</div>
    </div>
    <div class="card">
        <div class="label">System Uptime</div>
        <div class="stat">{{ uptime }} seconds</div>
    </div>
    <p>Version: <code>{{ version }}</code></p>
</body>
</html>
"""

@app.route('/')
def dashboard():
    if not bot_instance:
        return "System Initializing...", 503
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        latency=round(bot_instance.latency * 1000, 2),
        guild_count=len(bot_instance.guilds),
        uptime=int(time.time() - start_time),
        version=bot_instance.cfg.render_commit
    )

def run_server(port):
    app.run(host='0.0.0.0', port=port)

def keep_alive(bot):
    """Integrates the bot instance and starts the background thread."""
    global bot_instance
    bot_instance = bot
    server_thread = Thread(target=run_server, args=(bot.cfg.port,))
    server_thread.daemon = True
    server_thread.start()
