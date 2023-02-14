from django.db import models


class Message(models.Model):
    """
    Abstract model class for message that comes from different connectors.
    It must include a text, timestamp, author, and connector type (slack, discord). All connectors must inherit this class and fill it with data.

    > For slack:
    - text: event['text']
    - timestamp: datetime(event['ts'])
    - author: event['user']
    - connector: 'slack'
    """

    text = models.TextField()
    timestamp = models.DateTimeField()
    author = models.CharField(max_length=255)
    connector = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.text[:20]} - {self.author}'

    def save(self, *args, **kwargs):
        if not self.connector:
            raise NotImplementedError('Connector was not specified.')
        super().save(*args, **kwargs)


class Pattern(models.Model):
    """
    A pattern is a regex that is used to match a string

    Attributes:
        (id): generated automatically
        fixture: The regex pattern
        date_created: The date the pattern was created
        created_by: The user that created the pattern
        active: Whether the pattern is active or not
    """
    fixture = models.CharField(max_length=300)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.fixture


class Match(models.Model):
    """
    A 'match' is a link between pattern and message. It is created when a pattern is matched in a message.

    Attributes:
        (id): generated automatically
        pattern: The pattern that matched
        message: The message that matched
    """
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='match')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='match')

    def __str__(self):
        return f'{self.pattern} • {self.message.text[:20]}'

    class Meta:
        verbose_name_plural = 'Matches'
