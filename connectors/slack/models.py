from dlp.models import Message


class SlackMessage(Message):
    """
    A message from slack. Inherits from abstract django Message class.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connector = 'slack'

    class Meta:
        proxy = True
