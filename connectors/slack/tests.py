from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from dlp.handlers import PatternHandler
from dlp.models import Pattern


class SlackEventTestCase(TestCase):
    def setUp(self):
        from connectors.slack import views
        self.client = APIClient()
        self.url = '/connectors/slack/'
        self.user = User.objects.create(username='Admin')
        self.test_token = views.token
        self.test_event = {
            'type': 'message',
            'text': 'Test message with data.',
            'channel': 'test_channel',
            'user': 'test_user',
            'ts': 1644851200.0001001,
        }
        self.pattern1 = Pattern.objects.create(fixture='sensitive', active=True,
                                                  date_created=datetime.now(), created_by=self.user)

    def test_challenge(self):
        challenge_data = {'challenge': 'test_challenge'}
        response = self.client.post(self.url, data=challenge_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'test_challenge')

    def test_scan_no_match(self):
        response = self.client.post(self.url, data={'event': self.test_event}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'No matches found.')

    @patch.object(PatternHandler, 'scan')
    def test_slack_delete_message_and_reply(self, mock_scan):
        mock_scan.return_value = [(self.pattern1, (0, 4))]
        data = {
            'event': {
                'channel': 'test-channel',
                'user': 'test-user',
                'ts': '1234567890.123456',
                'text': 'test sensitive message'
            }
        }

        with patch('connectors.slack.views.client') as mock_client:
            mock_client.chat_delete.return_value = MagicMock()
            mock_client.chat_postMessage.return_value = MagicMock()
            response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 200)
        mock_scan.assert_called_once()

        mock_client.chat_postMessage.assert_called_once()
        mock_client.chat_delete.assert_called_once()