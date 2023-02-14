import re

from dlp.models import Pattern, Message


class PatternHandler:
    """
    Handler for pattern matching.
    Inputs a string and returns a list of patterns and addresses in style of string slicing that match the string."""

    def __init__(self):
        self.patterns = Pattern.objects.filter(active=True)

    def __check_fixtures(self, text: str) -> list[tuple[Pattern, tuple[int, int]]]:
        """
        Checks if the text matches any of the patterns in the database.

        :param text: The text to check
        :return: A list of tuples of the form (pattern, (start, end))
        """
        matches = []
        for pattern in self.patterns:
            for match in re.finditer(pattern.fixture, text):
                matches.append((pattern, match.span()))
        return matches

    def __log_matches(self, message: Message, matches: list):
        """
        Logs the matches in the database.

        :param message: The message that was matched
        :param matches: A list of tuples of the form (pattern, (start, end))
        """

        message.save()
        seen_patterns = set()

        for match in matches:  # (pattern, (start, end))
            # Create a new match object only if match for this pattern wasn't created
            if match[0].fixture not in seen_patterns:
                seen_patterns.add(match[0].fixture)
                match[0].match.create(message=message)


    def scan(self, message: Message, log=True) -> list[tuple[Pattern, tuple[int, int]]]:
        """
        Scan a string for patterns.

        If log is True, the matches will be logged in the database.
        Matches are represented as tuples of the form (pattern, (start, end)),
        where pattern is a Pattern object and (start, end) are the indices of the start
        and end of the match in the string.

        :param message: The Message object to scan
        :param log: Whether to log the scan into the database

        :return: list of tuples of the form (pattern, (start, end))
        """
        matches = self.__check_fixtures(message.text)
        if log and matches:
            self.__log_matches(message, matches)
        return matches
