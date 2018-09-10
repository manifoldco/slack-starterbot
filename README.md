# Demo Slackbot - Sending Texts via Till Mobile from Slack

This code demonstrates how you can combine Till Mobile and Slack to empower your slack users
to send sms messages out of slack to their phones.  Why?  Well sometimes your systems are on
fire and you just need to text out to your DevOps team, or, perhaps for more fun, you want to
do sms voting systems while you are having a retro meeting.  Or really, just for fun.

In this code we piece together Till Mobile, a slackbot, and the manifold cli to quickly get it all
plugged together.

## Quick Start
1. Clone this repo
2. Set up a project in Manifold called `till-mobile`
3. Provision a till mobile instance in manifold inside that project
4. Set up a slack Bot, add its key to your till mobile project as a custom resource
5. Turn on ngrok `ngrok 8181` and set PUBLIC_ADDR in your env to your incoming http url
5. `manifold run -p till-demo python tillbot.py`
6. Invite the bot into a channel and SMS away :-)

Send sms messages `@tillbot sms 10DIGITNUMBER Hello this is a test message`

Ask questions via sms `@tillbot ask 10DIGITNUMBER what is the meaning of life?`

# How to build the bot

## Requires

- [Manifold CLI](https://github.com/manifoldco/manifold-cli/blob/master/README.md)
- [manifold's till python client](https://github.com/manifoldco/pytill)
- [virtualenv](https://virtualenv.pypa.io/en/stable/)
- Based on a fork of [this demo Bot](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html)

## Set up your local environment

```
virtualenv till_slack
cd till_slack
source bin/active
pip3 install slackclient
pip install pytill
```

## Set up Till Mobile and Slack API

1. Set up a project in Manifold to store secrets in and add till mobile ```manifold projects create till-demo```
2. Go and get Till Moble `manifold create -p till-demo` and select `till` , choosing the plan you want (I chose `free`).  I also gave mine a fun name like 'till-demo-account' for the resource name.
```
 manifold create -p till-demo
✔ Product: till (Till)
✔ Plan: free (Free)
✔ Region: All Regions (all::global)
✔ Project: till-demo (Till Demo)
✔ New Resource Name: till-demo-account
✔ New Resource Title: Till Demo Account
An instance named "Till Demo Account" has been created!
```
3. Check to make sure its all good via:
```
$ manifold export -p till-demo
# Till Demo Account
API_KEY=<YOURAPIKEY>
USERNAME=<YOURUSERNAME>
```
4. For fun, we are going to create a custom resource called "Slack" while we are here, we can use this to store a Slack api key we will get a bit later. `manifold create -p till-demo -c`, I gave it a name like `till-demo-slack-api`
```
$ manifold create -p till-demo -c
✔ Project: till-demo (Till Demo)
✔ New Resource Name: till-demo-slack-api
✔ New Resource Title: Till Demo Slack Api
An instance named "Till Demo Slack Api" has been created!
```
5. Set up a [Slack App](https://api.slack.com/slack-apps)
  1. The app, for now, needs to have an incoming webhook and a bot name.  We will come back to add slack commands a bit later.
  2. Once done, you need to get the __Bot User Oauth Acsess Token__ from inside the "Oauth & Permissions" sidebar menu.
6. Then we need to put this __Oauth Acces Token__ into our custom resource we just made for future use.  You can do this via `manifold config set -r till-demo-slack-api SLACK_BOT_TOKEN=VALUE`
```
$ manifold config set -r till-demo-slack-api SLACK_BOT_TOKEN=<SLACK_SIGNING_SECRET>
Your configuration has been updated.
```

## Sanity Check
Lets sanity check we can actually talk to slack using manifold cli, with virtualenv active (`source bin/active`)
1. `manifold run -p till-demo python`
2. And inside the Python REPL enter the following:
```
import os
from pytill import pytil
from slackclient import SlackClient
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN', None))
slack_client.api_call("api.test")
pytill.send_message(['YOURNUMBERHRE'], 'I am sending a till message isnt that cool!')
```
This should return back something like:
```
{'ok': True, 'args': {'token': 'xoxb-<yourtokenhere>'},
```
As well as a test txt message.  We now know we can talk to slack as well as send texts, time to plug it all together.


## The code
You can clone this repo to get the working code, I'll explain a bit of the logic here,

1. We need to listen to slack and watch for our bot to be mentioned.
2. From there, parse the command we are looking for and send the message.
3. To send the message, use [pytill](https://github.com/manifoldco/pytill) from `pytill import pytill`
4. To parse and send the SMS  command (Line [59](https://github.com/manifoldco/tillmobile-demo/blob/master/tillbot.py#L59)):
where COMMAND_SMS is `COMMAND_SMS = "sms"` (Line [22](https://github.com/manifoldco/tillmobile-demo/blob/master/tillbot.py#L22))

5. Now we simply turn this code on `manifold run -p till-demo python tillbot.py`

# Test it out in Slack
- In slack, go and invite your bot into a channel (I called mine tillbot, I know, original)
- Go ahead and send yourself a message `@tillbot sms 10DIGITNUMBER Hello this is a test message` and that number should get a nice shinny text message!

## Make it bi-direction

At this point the bot can send sms messages, amazing, but what if we want to ask questions and get the inbound sms back?  To get this we need to set up an incoming webhook (using flask in this example) and a few more bits and pieces.

Take a look at function `send_sms_question` (Line [80](https://github.com/manifoldco/tillmobile-demo/blob/master/tillbot.py#L80)) to see how we now leverage `pytill.make_question` in combination with adding a webhook `app.route(WEBHOOK_ADDR`

Lastly you need to set PUBLIC_ADDR in your env, if locally testing use `ngrok` to get yourself an incoming url.

Now you can ask questions via:
`@tillbot ask 10DIGITNUMBER what do you want for lunch`

The number will get the sms, and be able to reply with `new phone, who dis?`, or perhaps an actual answer if they so choose :-)

## Possible Improvements
- Use slack's api to pull accept @mentions instead of actual numbers, and pull their phone number from the profile to send the messages :-)


# Credits
Based on a fork of `slack-starterbot` by Matt Makai

`A simple Python-powered starter Slack bot`
Read [the tutorial](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html)
for a full overview.
