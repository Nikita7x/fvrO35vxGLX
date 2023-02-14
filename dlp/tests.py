from datetime import datetime

from django.test import TestCase
from dlp.models import Pattern, Message
from .handlers import PatternHandler

class PatternHandlerTestCase(TestCase):
    def setUp(self):
        # Create some patterns to use in the tests
        from django.contrib.auth.models import User
        self.user = User.objects.create(username='Admin')

        self.pattern1 = Pattern.objects.create(fixture='hello', active=True,
                                               date_created=datetime.now(), created_by=self.user)
        self.pattern2 = Pattern.objects.create(fixture='world', active=True,
                                               date_created=datetime.now(), created_by=self.user)
        self.pattern3 = Pattern.objects.create(fixture='python', active=False,
                                               date_created=datetime.now(), created_by=self.user)
        self.pattern4 = Pattern.objects.create(fixture='django', active=True, date_created=datetime.now(), created_by=self.user)

    def test_scan(self):
        # Test that the scan method correctly identifies patterns in a message
        handler = PatternHandler()
        message = Message.objects.create(
            text='hello world!',
            author='andrew',
            connector='testcase',
            timestamp=datetime.now()
        )

        expected_matches = [(self.pattern1, (0, 5)), (self.pattern2, (6, 11))]
        matches = handler.scan(message)
        self.assertEqual(matches, expected_matches)

    def test_scan_with_inactive_patterns(self):
        # Test that the scan method correctly handles inactive patterns
        handler = PatternHandler()
        message = Message.objects.create(
            text='hello python!',
            author='andrew',
            connector='testcase',
            timestamp=datetime.now()
        )
        expected_matches = [(self.pattern1, (0, 5))]
        matches = handler.scan(message)
        self.assertEqual(matches, expected_matches)

    def test_scan_without_logging(self):
        # Test that the scan method does not log matches when log=False
        handler = PatternHandler()
        message = Message.objects.create(
            text='hello django app!',
            author='andrew',
            connector='testcase',
            timestamp=datetime.now()
        )
        handler.scan(message, log=False)
        self.assertFalse(self.pattern4.match.exists())

    def test_scan_with_logging(self):
        # Test that the scan method logs matches when log=True
        handler = PatternHandler()
        message = Message.objects.create(
            text='hello dear django!',
            author='andrew',
            connector='testcase',
            timestamp=datetime.now()
        )
        handler.scan(message, log=True)
        self.assertTrue(self.pattern4.match.exists())