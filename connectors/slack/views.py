from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView
from slack_sdk import WebClient

from .models import SlackMessage
from dlp.handlers import PatternHandler


### DANGER ZONE ###
# token needs to be USER-token, not bot-token. User tokens start with "xoxp-"
# In terms of MVP I'm saving this token in the code, but in the future it should be moved to .env file or stored in encrypted database.
token = "xoxp-1234567890-1234567890-1234567890-1234567890"
### ----------- ###

client = WebClient(token=token)

class SlackEvent(APIView):
    def post(self, request):
        if 'challenge' in request.data:
            # When Slack sends a challenge, we must respond with the challenge. It is necessary for Slack to verify that the endpoint is valid.
            return Response(request.data['challenge'])

        if 'text' not in request.data['event']:
            return Response('No text found. Message may me modified')

        message = SlackMessage(
            text=request.data['event']['text'],
            timestamp=datetime.fromtimestamp(float(request.data['event']['ts'])),
            author=request.data['event']['user'],
        )

        matches = PatternHandler().scan(message)  # <- Facade

        if not matches:
            return Response('No matches found.')
        # I've decided not to use separate files and classes for "business logic", so I'll leave these methods here.
        client.chat_postMessage(
            channel=request.data['event']['channel'],
            text='Текст сообщения содержал потенциально важные данные.',
            thread_ts=request.data['event']['ts'],
        )
        client.chat_delete(
            channel=request.data['event']['channel'],
            ts=request.data['event']['ts'],
        )
        return Response('Message deleted.')
