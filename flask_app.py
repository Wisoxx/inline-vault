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

    try:
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.readlines()

        colored_logs = []
        for line in log_content:
            line = line.rstrip()

            if not line:
                colored_logs.append('<br>')
                continue

            # Split based on spaces to extract timestamp, level, and message
            parts = line.split(maxsplit=3)
            if len(parts) >= 3:
                timestamp = " ".join(parts[:2])
                level = parts[2].strip(":")
                message = parts[3] if len(parts) > 3 else ""
                color_class = level.lower()  # Define class based on log level

                # Apply the color class to the log entry
                colored_logs.append(
                    f'<span class="{color_class}">{timestamp} <strong>{level}</strong>: {message}</span><br>'
                )
            else:
                colored_logs.append(f'<span class="default">{line}</span><br>')

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
                                background-color: #000;
                                color: #fff;
                            }
                            .log-content {
                                flex: 1;
                                overflow-y: auto;
                                padding: 10px;
                                background-color: #000;
                            }
                            .log-content pre {
                                white-space: pre-wrap;
                                word-wrap: break-word;
                            }
                            .debug { color: lightblue; }
                            .info { color: lightgreen; }
                            .warning { color: orange; }
                            .error { color: red; }
                            .critical { color: magenta; }
                            .default { color: white; }
                        </style>
                    </head>
                    <body>
                        <div class="log-content">
                            <pre>{{ colored_logs|safe }}</pre>
                        </div>
                        <script>
                            document.querySelector('.log-content').scrollTop = document.querySelector('.log-content').scrollHeight;
                        </script>
                    </body>
                    </html>
                ''', colored_logs=''.join(colored_logs))

    except Exception as e:
        return Response(f"Error reading log file: {str(e)}", status=500)
