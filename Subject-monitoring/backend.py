import logging

import flask
from flask import request
from terra.base_client import Terra

logging.basicConfig(level=logging.INFO)

_LOGGER = logging.getLogger("app")

app = flask.Flask(__name__)


webhook_secret = "53c98e6ad3ee15ca47f3d8fa0a38d64290f7ef82e0e73881"
dev_id='4actk-squadsync-testing-amtOIiHNTn'
api_key = 'OScAShz-BovbJIwU8-Ls0lvbCVSLIG63'

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


if __name__ == "__main__":
    app.run()