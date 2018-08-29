import os
import time
import re
import json
from slackclient import SlackClient
from pytill import pytill


# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
COMMAND_SMS = "sms"
COMMAND_ASK = "ask"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(COMMAND_SMS)

    # Finds and executes the given command, filling in response
    response = None

    # Command is to send an SMS
    if command.startswith(COMMAND_SMS):
        response = send_sms(command)
    
        # Command is to send an SMS
    if command.startswith(COMMAND_ASK):
        response = send_sms_question(command, webhook)


    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def send_sms(command):
    data = command.split(" ", 2) # maxsplit
    pytill.send_message([data[1]], data[2])
    response = "Text sent to {}".format(data[1])
    return response

def send_sms_question(command, webhook):
    data = command.split(" ", 2) # maxsplit
    question = pytill.make_question(data[2], "{}-tag".format(data[2]), webhook)
    pytill.send_question([data[1]], [question], "{}-project-tag".format(data[2]))
    response = "Question sent to {} listening for answers...".format(data[1])
    return response

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
