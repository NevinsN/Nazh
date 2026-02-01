from flask import Flask, render_template_string
from threading import Thread
from modules.metrics import metrics
import time
from datetime import datetime

app = Flask(__name__)
bot_instance = None
start_time = time.time()

BASE_STYLE = """
<style>
    body { font-family: 'Inter', sans-serif; background: #0f0f0f; color: #e0e0e0; padding: 40px; }
    .container { max-width: 900px; margin: auto; }
    .card { background: #1a1a1a; padding: 25px; border-radius: 12px; margin-bottom: 20px; border-left: 6px solid #5865F2; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .stat { font-size: 32px; font-weight: 800; color: #ffffff; }
    .label { color: #b9bbbe; font-size: 13px; text-transform: uppercase; font-weight: 600; }
    .status-badge { color: #3ba55c; background: rgba(59, 165, 92, 0.1); padding: 5px 12px; border-radius: 20px; font-size: 14px; }
    .btn { background: #5865F2; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; }
</style>
"""

DASHBOARD_TEMPLATE = BASE_STYLE + """
<div class="container">
    <h1>Nazh Engine <span class="status-badge">● System Online</span></h1>
    <div class="card">
        <div class="label">Infrastructure Integrity</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
            <div><div class="label">API Latency</div><div class="stat">{{ latency }}ms</div></div>
            <div><div class="label">Active Guilds</div><div class="stat">{{ guild_count }}</div></div>
            <a href="/guilds" class="btn">Inventory Details</a>
        </div>
    </div>
    <div class="card" style="border-left-color: #faa61a;">
        <div class="label">Golden Signals (Traffic & Reliability)</div>
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <div><div class="label">Success Rate</div><div class="stat" style="color:#3ba55c;">{{ success_rate }}%</div></div>
            <div><div class="label">Total Rolling Volume</div><div class="stat">{{ roll_total }}</div></div>
        </div>
    </div>
</div>
"""

@app.route('/')
def dashboard():
    if not bot_instance:
        return "System Initializing...", 503
    
    stats = metrics.get_report()
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        latency=round(bot_instance.latency * 1000, 2) if bot_instance.latency else 0,
        guild_count=len(bot_instance.guilds),
        uptime=int(time.time() - start_time),
        
        # Use .get(key, default) to prevent KeyErrors
        build_count=stats.get("build_requests", 0),
        roll_total=stats.get("roll_total", 0),
        success_rate=stats.get("roll_success_rate", 100.0),
        
        version=bot_instance.cfg.render_commit,
        last_updated=datetime.now().strftime("%H:%M:%S")
    )


@app.route('/guilds')
def guilds():
    # Similar template logic using BASE_STYLE...
    pass

def keep_alive(bot):
    global bot_instance
    bot_instance = bot
    Thread(target=lambda: app.run(host='0.0.0.0', port=bot.cfg.port)).start()
