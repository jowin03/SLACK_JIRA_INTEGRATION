# Slack to Jira Integration 

 - This project demonstrates how to create a Slack app that listens to messages in a Slack channel and creates an issue in a Jira project via a webhook. The integration includes error handling for incorrect inputs.

## Table of Contents

 - Prerequisites
 - Setting Up Slack
 - Setting Up Jira
 - Creating the Webhook
 - Developing the Script for Integration
 - Running the Application
 - Error Handling
 - References

### Prerequisites

 - A free Slack account
 - A Jira cloud instance
 - Basic knowledge of Python
 - Flask installed in your Python environment
 - Slack-sdk installed in your Python environment 

### Setting Up Slack

 #### Create a Slack Account:
  - If you don’t have a Slack account, sign up for a free account at Slack.

 #### Create a Slack App:
  - Go to the Slack API: Your Apps page.
  - Click "Create New App."
  - Choose "From scratch."
  - Enter an App Name and select the workspace where you want to develop your app.

 #### Enable Event Subscriptions:
  - In your app's settings, go to "Event Subscriptions."
  - Turn on "Enable Events."
  - Set the "Request URL" to the URL where your Flask app will be running (e.g., https://yourdomain.com/slack/events).
  - Add the message.channels event under "Subscribe to Bot Events."

 #### Install the App to your Workspace:
  - Go to "OAuth & Permissions" and click "Install App to Workspace."
  - Authorize the app for your workspace.

### Setting Up Jira

 #### Create a Jira Cloud Instance:
  - Sign up for a free Jira cloud account at Atlassian Jira.

 #### Create a Jira Project:
  - Once logged in, create a new project and note down the project key.

### Creating the Webhook
 
 #### Generate a Jira API Token:
  - Go to your account settings in Jira and generate an API token. Save this token securely.

 #### Set Up the Webhook in Jira:
  - Go to "System" in Jira settings and click on "WebHooks."

 #### Create a new webhook with the following settings:
  - Name: Slack to Jira
  - URL: https://yourdomain.com/jira/webhook
  - Events: Choose events relevant to issue creation if needed

### Developing the Script for Integration

 #### Create the Flask Application:
  - Create a app.py file with the correct content.

### Running the Application

 #### Start the Flask App:
  - python app.py

 #### Expose the Flask App:
  - If running locally, use a tool like ngrok to expose your local server to the internet:
  - ngrok http 3000 or 5000
  - Update the Slack Event Subscription URL and Jira WebHook URL with the ngrok URL.

### Error Handling

 - The Flask app includes basic error handling to respond with appropriate messages if the Jira issue creation fails.

### References

 - Slack API Documentation
 - Jira API Documentation
 - Flask Documentation
