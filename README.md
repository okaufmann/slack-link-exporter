# Slack Message Exporter for Raindrop.io

## Project Description
This Python script exports messages from a specified Slack channel, focusing on messages containing URLs. It outputs the data in a CSV format that can be imported into Raindrop.io. The script uses Slack's API and requires specific permissions to access channel history and user details.

## Requirements
- Python 3.x
- Pip (Python package manager)

## Installation
1. **Clone or Download the Repository**
   - Clone this repository to your local machine or download the source code.

2. **Install Required Packages**
   - Navigate to the project directory and install the required Python packages:
     ```bash
     pip install -r requirements.txt
     ```

3. **Setting Up Environment Variables**
   - Rename the `.env.example` file to `.env`.
   - Fill in the `SLACK_TOKEN` and `CHANNEL_ID` with your Slack API token and the ID of the channel you want to export messages from.

## Usage
1. **Run the Script**
   - Execute the script with Python:
     ```bash
     python3 import.py
     ```
   - The script will generate a CSV file named `slack_links.csv` in the project directory.

## Creating a Slack App
1. **Create a New App**
   - Go to [Your Apps](https://api.slack.com/apps) on Slack API and create a new app.
   - Choose the workspace where you want to install your app.

2. **Add Permissions**
   - Under the **OAuth & Permissions** section, add the following scopes:
     - `users:read` (To read user details for user name resolution)
     - `channels:history` (To access channel message history)

3. **Install the App**
   - Install the app to your workspace.
   - Upon installation, you'll receive an OAuth Access Token. Use this token in your `.env` file as `SLACK_TOKEN`.

4. **Find Your Channel ID**
   - Navigate to the Slack channel from which you want to export messages.
   - The channel ID can be found in the URL: `https://app.slack.com/client/[workspace_id]/[channel_id]`

## Environment Variables
- `SLACK_TOKEN`: Your Slack App's OAuth Access Token.
- `CHANNEL_ID`: The ID of the Slack channel you want to export messages from.
- (Optional) Define exclusion patterns for URLs in the `.env` file.

---

## Manifest for Slack App
To create a Slack App manifest:

1. Navigate to [Your Apps](https://api.slack.com/apps) on the Slack API.
2. Create a new app and choose JSON manifest.
3. Use the following template and modify it as per your requirements:

```json
{
  "display_information": {
    "name": "Slack Message Exporter",
    "description": "An app to export messages from Slack channels.",
    "background_color": "#4A154B"
  },
  "features": {
    "bot_user": {
      "display_name": "Slack Exporter Bot",
      "always_online": true
    }
  },
  "oauth_config": {
    "scopes": {
      "bot": ["users:read", "channels:history"]
    }
  },
  "settings": {
    "event_subscriptions": {
      "request_url": "https://yourapp.com/slack/events",
      "bot_events": ["message.channels"]
    },
    "interactivity": {
      "is_enabled": false
    },
    "org_deploy_enabled": false,
    "socket_mode_enabled": false,
    "token_rotation_enabled": false
  }
}
```

4. Save the manifest and follow the prompts to complete the creation of your Slack App.

---
