from flask import Flask # import Flask
from threading import Thread # import Thread

app = Flask(__name__) # Initialize Flask

# route for root URL
@app.route('/')
# Runs when root is activated
def home():
    return "I'm alive!"

# Starts Flask development server and makes it accessible to external sources
def run_server():
    app.run(host='0.0.0.0', port = 8080) # Accessible externally

# Creates thread
def keep_alive():
    server_thread = Thread(target = run_server)
    server_thread.daemon = True # allows main to close regardless of thread running
    server_thread.start()