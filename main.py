import os
import json
import logging
from flask import Flask, request, jsonify
import requests
from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()

# Slack and Jira configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_VERIFICATION_TOKEN = os.getenv('SLACK_VERIFICATION_TOKEN')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY')
PORT = os.getenv('port')

slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Logger setup
logging.basicConfig(level=logging.INFO)

# To keep track of processed event IDs
processed_event_ids = set()

def create_jira_issue(issue_summary, priority, reporter):
    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
   
    # Atlassian Document Format (ADF) for the description field
    description_adf = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": issue_summary
                    }
                ]
            }
        ]
    }
   
    payload = {
        "fields": {
            "project": {
                "key": JIRA_PROJECT_KEY
            },
            "summary": issue_summary,
            "description": description_adf,
            "issuetype": {
                "name": "Task"
            },
            "priority": {
                "name": priority
            },
            "reporter": {
                "name": reporter
            }
        }
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers, auth=auth)
   
    if response.status_code == 201:
        logging.info("Jira issue created successfully.")
        return response.json()
    else:
        logging.error(f"Failed to create Jira issue: {response.text}")
        return None


@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json

    # Handle URL verification challenge
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    # Verify request token
    if 'token' not in data or data['token'] != SLACK_VERIFICATION_TOKEN:
        return jsonify({'error': 'Invalid request token'}), 403

    # Handle the Slack event
    if 'event' in data:
        event = data['event']
        event_id = event.get('event_ts')

        if event_id in processed_event_ids:
            logging.info("Duplicate event detected; skipping.")
            return jsonify({'status': 'duplicate'}), 200

        processed_event_ids.add(event_id)

        if event['type'] == 'message' and 'bot_id' not in event:
            user = event['user']
            text = event['text']
            channel = event['channel']

            logging.info(f"Received message from {user}: {text}")

            try:
                # Initialize variables
                issue = None
                priority = None
                reporter = None

                # Split message by lines and process each line
                lines = text.strip().split('\n')
                for line in lines:
                    # Ensure there is a colon to split on
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if key.strip().lower() == 'issue':
                            issue = value.strip()
                        elif key.strip().lower() == 'priority':
                            priority = value.strip()
                        elif key.strip().lower() == 'reporter':
                            reporter = value.strip()

                # If none of the fields were found, it's an invalid format
                if issue is None and priority is None and reporter is None:
                    response_text = "Error: Invalid input format. Please provide an 'Issue', 'Priority', and 'Reporter'."
                elif not issue:
                    response_text = "Error: 'issue' field is missing. Please provide an 'issue' in your message."
                elif not priority:
                    response_text = "Error: 'priority' field is missing. Please provide a 'priority' in your message."
                elif not reporter:
                    response_text = "Error: 'reporter' field is missing. Please provide a 'reporter' in your message."
                else:
                    jira_issue = create_jira_issue(issue, priority, reporter)
                    if jira_issue:
                        response_text = f"Jira issue created successfully: {jira_issue['key']}"
                    else:
                        response_text = "Failed to create Jira issue."

            except Exception as e:
                logging.error(f"Error processing message: {e}")
                response_text = (
                    "Error: Invalid input format. Please provide an 'Issue', 'Priority', and 'Reporter'."
                )

            try:
                slack_client.chat_postMessage(channel=channel, text=response_text)
            except SlackApiError as e:
                logging.error(f"Error sending message to Slack: {e.response['error']}")

    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(port=PORT, debug=True)

