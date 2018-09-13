import os
import requests
import json

from flask import Flask, jsonify, request, make_response
from slackclient import SlackClient

SLACK_TOKEN = os.environ.get('SLACK_API')

app = Flask(__name__)

slack_client = SlackClient(SLACK_TOKEN)

incidence_ts = {}

@app.route('/users/', methods=['GET'])
def users():
    users = slack_client.api_call('users.list')
    return jsonify(dict(users=users['members'])), 200

@app.route('/channels/', methods=['GET'])
def channels():
    channels = slack_client.api_call('channels.list')
    return jsonify(dict(
        channels=channels['channels']
    )), 200

@app.route('/send-message/', methods=['POST'])
def sendmessage():
    channels = slack_client.api_call('channels.list')
    for channel in channels['channels']:
        if channel['id'] == 'C2AB2R51D':
            send_message = slack_client.api_call(
                'chat.postMessage',
                username='BoluBot',
                icon_emoji=':robot_face',
                channel='C2AB2R51D',
                text='Welcome to Andela!\nWe are here to change the World!'
            )
            return jsonify(dict(response=send_message)), 200


@app.route('/api/v1/incidence-reports', methods=['POST'])
def respon():
    if request.form.get('payload') == None:
        channel_id = request.form.get('channel_id', None)
        user_id = request.form.get('user_id', None)
        slack_client.api_call(
            "chat.postEphemeral",
            username='BoluBot',
            channel=channel_id,
            user=user_id,
            response_type='ephemeral',
            text="Would you like to log incident report?",
            attachments=[
                {
                    "fallback": "You are unable to choose a game",
                    "callback_id": "choice_made",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "game",
                            "text": "Yes",
                            "type": "button",
                            "value": "yes"
                        },
                        {
                            "name": "game",
                            "text": "No",
                            "type": "button",
                            "value": "no"
                        },
                    ]
                }
            ]
        )
        return make_response('', 200)

    req = request.form.get('payload', None)
    res_ = json.loads(req)

    if res_['type'] == 'dialog_cancellation':
        return make_response('', 200)

    if res_['type'] == 'interactive_message':
        incidence_ts['message_ts'] = res_['message_ts']
        if res_['callback_id'] == 'choice_made':
            if res_['actions'][0]['value'] == 'yes':
                slack_client.api_call(
                    'dialog.open',
                    trigger_id=res_['trigger_id'],
                    dialog={
                        "title": "Andela Resources Tracker",
                        "submit_label": "Submit",
                        "notify_on_cancel": True,
                        "callback_id": "{}_incidence_report_1".format(
                            res_['user']['id']),
                        "elements": [
                            {
                                'label': 'Asset',
                                'type': 'text',
                                'name': 'title',
                                'value': '',
                                'hint': '30 second summary of the problem',
                            },
                            {
                                'label': 'Incident type',
                                'type': 'select',
                                'name': 'incident_type',
                                'options': [
                                    { 'label': 'Loss', 'value': 'Loss' },
                                    { 'label': 'Damage', 'value': 'Damage' }
                                ]
                            },
                            {
                                'label': 'Incident location',
                                'type': 'text',
                                'name': 'incident_location',
                                'hint': '30 second summary of the problem',
                            },
                            {
                                'label': 'Incident description',
                                'type': 'textarea',
                                'name': 'incident_description',
                                'optional': True,
                            },
                            {
                                'label': 'Injuries sustained',
                                'type': 'textarea',
                                'name': 'injuries_sustained',
                                'optional': True,
                            },
                        ]
                    }
                )
                return make_response('', 200)
            return make_response('', 200)

    if res_['type'] == 'dialog_submission':
        slack_client.api_call(
            "chat.postEphemeral",
            username='BoluBot',
            channel=res_['channel']['id'],
            user=res_['user']['id'],
            response_url= res_['response_url'],
            response_type='ephemeral',
            text="Continue with other information?",
            attachments=[
                {
                    "fallback": "You are unable to choose a game",
                    "callback_id": "choice_made",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "game",
                            "text": "Continue",
                            "type": "button",
                            "value": "continue"
                        },
                        {
                            "name": "game",
                            "text": "Dismiss",
                            "type": "button",
                            "value": "dismiss"
                        },
                    ]
                }
            ]
        )
        return make_response('', 200)



if __name__ == '__main__':
    app.run(debug=True, port=8000)

# https://kolawole.slack.com/archives/C2AB2R51D/p1529008457000112
