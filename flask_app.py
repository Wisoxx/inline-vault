from flask import Flask, request, Response, render_template_string
from bot import Bot, telepot
import urllib3
from urllib3.util.retry import Retry
from logger import setup_logger
import os
from dotenv import load_dotenv


class LoggingRetry(Retry):  # overriding class to have logs when connection errors occur
    def __init__(self, *args, **kwargs):
        self.retry_count = 0
        super().__init__(*args, **kwargs)

    def increment(self, *args, **kwargs):
        self.retry_count += 1
        logger = setup_logger(__name__)
        logger.warning(f"Retrying request {self.retry_count}")
        return super().increment(*args, **kwargs)


project_folder = os.path.expanduser('~/mysite')
load_dotenv(os.path.join(project_folder, '.env'))

proxy_url = "http://proxy.server:3128"
retry_strategy = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
)
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=retry_strategy, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=retry_strategy, timeout=30))

TOKEN = os.getenv("TELEGRAM_TOKEN")
SECRET = os.getenv("SECRET")
SITE = os.getenv("SITE_URL")

bot = Bot(TOKEN)
bot.setWebhook(SITE + SECRET, max_connections=1)

app = Flask(__name__)


@app.route('/{}'.format(SECRET), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    bot.handle_update(update)
    return "OK"


@app.route(f'/{SECRET}/logs', methods=["GET"])
def view_logs():
    log_file_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs', 'app.log')
    level_colors = {
        "DEBUG": "lightblue",
        "INFO": "lightgreen",
        "WARNING": "orange",
        "ERROR": "red",
        "CRITICAL": "magenta",
    }

    try:
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.readlines()  # Read the log file line by line

        colored_logs = []
        entry_lines = []
        current_color = "white"

        for line in log_content:
            line = line.rstrip()

            # Detect the start of a new log entry by timestamp format
            if line.startswith("2024-") and len(entry_lines) > 0:
                # Process the accumulated entry
                entry_text = "\n".join(entry_lines)

                # Extract level and determine color
                parts = entry_lines[0].split(maxsplit=3)
                if len(parts) >= 3:
                    level = parts[2].strip(":")
                    current_color = level_colors.get(level, "white")

                # Append the entry with the determined color
                colored_logs.append(
                    f'<span style="color: {current_color};">{entry_text}</span><br>'
                )

                # Reset for the next entry
                entry_lines = []

            # Accumulate lines for the current entry
            entry_lines.append(line)

        # Process the last entry
        if entry_lines:
            entry_text = "\n".join(entry_lines)
            colored_logs.append(
                f'<span style="color: {current_color};">{entry_text}</span><br>'
            )

        # Join the logs for rendering and wrap in the template
        return render_template_string('''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Log Viewer</title>
                        <style>
                            body {
                                display: flex;
                                flex-direction: column;
                                height: 100vh;
                                margin: 0;
                                background-color: #000;  /* Set the background to black */
                                color: #fff;              /* Set the text color to white */
                            }
                            .log-content {
                                flex: 1;
                                overflow-y: auto;
                                padding: 10px;
                                border: 1px solid #ccc;
                                background-color: #000;  /* Keep log content background black */
                            }
                            pre {
                                white-space: pre-wrap;   /* Ensure long lines wrap */
                                word-wrap: break-word;   /* Break words to fit the container */
                            }
                        </style>
                    </head>
                    <body>
                        <div class="log-content">
                            <pre>{{ colored_logs|safe }}</pre>  <!-- Render the colored logs safely -->
                        </div>
                        <script>
                            // Scroll to the bottom of the log content
                            document.querySelector('.log-content').scrollTop = document.querySelector('.log-content').scrollHeight;
                        </script>
                    </body>
                    </html>
                ''', colored_logs=''.join(colored_logs))  # Join the colored logs for rendering

    except Exception as e:
        return Response(f"Error reading log file: {str(e)}", status=500)
