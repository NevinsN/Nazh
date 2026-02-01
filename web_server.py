from flask import Flask, render_template_string
from threading import Thread
from modules.metrics import metrics
import time
from datetime import datetime
import logging

app = Flask(__name__)
# Global reference to the bot instance
bot_instance = None
start_time = time.time()
logger = logging.getLogger("web_server")

# Professional Dark-Mode Dashboard Styling
BASE_STYLE = """
<style>
    body { font-family: 'Inter', -apple-system, sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 40px; line-height: 1.6; }
    .container { max-width: 900px; margin: auto; }
    .card { background: #1a1a1a; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #5865F2; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .stat { font-size: 32px; font-weight: 800; color: #ffffff; margin: 5px 0; }
    .label { color: #b9bbbe; font-size: 13px; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .status-badge { color: #3ba55c; background: rgba(59, 165, 92, 0.1); padding: 5px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; }
    .btn { background: #5865F2; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; display: inline-block; transition: background 0.2s; }
    .btn:hover { background: #4752c4; }
    code { background: #2f3136; padding: 2px 6px; border-radius: 4px; color: #7289da; }
    .footer { text-align: center; color: #4f545c; font-size: 12px; margin-top: 40px; }
</style>
"""

DASHBOARD_TEMPLATE = BASE_STYLE + """
<div class="container">
    <h1>Nazh Engine <span class="status-badge">● System Online</span></h1>
    
    <div class="card">
        <div class="label">Infrastructure Integrity</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <div>
                <div class="label">API Latency</div>
                <div class="stat">{{ latency }}ms</div>
            </div>
            <div>
                <div class="label">Active Guilds</div>
                <div class="stat">{{ guild_count }}</div>
            </div>
            <a href="/guilds" class="btn">Inventory Details</a>
        </div>
    </div>

    <div class="card" style="border-left-color: #faa61a;">
        <div class="label">Golden Signals (Traffic & Reliability)</div>
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <div>
                <div class="label">Success Rate</div>
                <div class="stat" style="color:#3ba55c;">{{ success_rate }}%</div>
            </div>
            <div>
                <div class="label">Total Rolling Volume</div>
                <div class="stat">{{ roll_total }}</div>
            </div>
            <div>
                <div class="label">Pool Builds</div>
                <div class="stat">{{ build_count }}</div>
            </div>
        </div>
    </div>

    <div class="footer">
        Version Trace: <code>{{ version }}</code> | Telemetry Sync: {{ last_updated }}
    </div>
</div>
"""

GUILDS_TEMPLATE = BASE_STYLE + """
<div class="container">
    <a href="/" style="color: #5865F2; text-decoration: none; font-weight: bold;">← Return to Dashboard</a>
    <h1 style="margin-top: 20px;">Active Guild Connectivity ({{ count }})</h1>
    {% for guild in guilds %}
    <div class="card" style="border-left-color: #3ba55c;">
        <div style="font-size: 18px; font-weight: bold;">{{ guild.name }}</div>
        <div style="color: #b9bbbe; font-family: monospace; font-size: 12px;">ID: {{ guild.id }}</div>
    </div>
    {% else %}
    <p>No guilds currently connected or bot is still initializing.</p>
    {% endfor %}
</div>
"""

@app.route('/')
def dashboard():
    if not bot_instance:
        return "<h3>System Booting: Handshaking with Discord Gateway...</h3>", 503
    
    # Get report with built-in math from metrics.py
    stats = metrics.get_report()
    
    # Render with .get() fail-safes to prevent 500 errors
    return render_template_string(
        DASHBOARD_TEMPLATE,
        latency=round(bot_instance.latency * 1000, 2) if bot_instance.latency else 0,
        guild_count=len(bot_instance.guilds) if hasattr(bot_instance, 'guilds') else 0,
        roll_total=stats.get("roll_total", 0),
        success_rate=stats.get("roll_success_rate", 100.0),
        build_count=stats.get("build_requests", 0),
        version=(bot_instance.cfg.render_commit[:7] if hasattr(bot_instance, 'cfg') and bot_instance.cfg.render_commit else "v1.0.0"),
        last_updated=datetime.now().strftime("%H:%M:%S")
    )

@app.route('/guilds')
def guilds():  # Make sure this matches the route name 'guilds'
    is_ready = bot_instance and bot_instance.is_ready()
    guild_list = bot_instance.guilds if is_ready else []
    
    return render_template_string(
        GUILDS_TEMPLATE,
        guilds=guild_list,
        count=len(guild_list)
    )


def run_server(port):
    """Starts the Flask app on the assigned Render port."""
    app.run(host='0.0.0.0', port=port, threaded=True)

def keep_alive(bot):
    """Links the bot instance and spawns the web sidecar thread."""
    global bot_instance
    bot_instance = bot
    server_thread = Thread(target=run_server, args=(bot.cfg.port,))
    server_thread.daemon = True
    server_thread.start()
