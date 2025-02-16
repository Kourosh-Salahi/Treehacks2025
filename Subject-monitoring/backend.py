import logging

import flask
from flask import request
from terra.base_client import Terra
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()

# Access the variable
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins





logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger("app")

app = flask.Flask(__name__)


webhook_secret = "53c98e6ad3ee15ca47f3d8fa0a38d64290f7ef82e0e73881"
dev_id='4actk-squadsync-testing-amtOIiHNTn'
api_key = os.getenv("API_KEY")

terra = Terra(api_key=api_key, dev_id=dev_id, secret=webhook_secret)

@app.route("/ConsumeTerraWebhook", methods=['POST'])
def consume_terra_webhook():
    body = request.get_json()


    verified = terra.check_terra_signature(request.data.decode("utf-8"), request.headers['terra-signature'])

    if not verified:
        _LOGGER.info('NO')
        return flask.Response(status=403)


    _LOGGER.info("Recieved Terra Webhook: %s",  body)

    return flask.Response(status=200)


@app.route('/authenticate', methods=['GET'])
def authenticate():
    widget_response=terra.generate_widget_session(providers=[], reference_id='1234')
    widget_url = widget_response.get_json()['url']
    return flask.Response(f"<button onclick =\"location.href='{widget_url}'\"> Authenticate with Apple Watch</button>", mimetype="text/html")


@app.route('/backfill', methods=['GET'])
def backfill():


    user_id = "12b5f134-a04b-4151-8812-6528982d23da"

    terra_user = terra.from_user_id(user_id)

    heart_data = terra_user.get_activity(start_date=datetime.datetime.now() - datetime.timedelta(days=7), end_date=datetime.datetime.now())  

    return heart_data.get_json()

if __name__ == "__main__":
    app.run()