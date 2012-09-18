import re
from common import fuzzy_match

class CommandHistory:
    """
    Handle all things related to storing and navigating the command history
    """
    def __init__(self):
        # The actual command list
        self.list = []

        # The current search filter
        self.filter = ''

        # A filtered list based on the current filter
        self.filtered_list = []

        # A trail of visited indices (while navigating)
        self.trail = []

    def start(self, line):
        """
        Start history navigation
        """
        #print '\n\nStart\n\n'
        self.filter = line

        words = re.findall('[a-zA-Z0-9]+', line) # Split the filter into words
        boundary = '[\\s\\.\\-\\\\_]+'   # Word boundary characters

        # Regexp patterns used for matching; strongest first, weakest last
        patterns = [
            # Exact string match (strongest, these will be the first results)
            '(' + re.escape(line) + ')',

            # Prefixes match for each word in the command
            '^' + boundary.join(['(' + word + ')[a-zA-Z0-9]*' for word in words]) + '$',

            # Prefixes match for some words in the command
            boundary.join(['(' + word + ')[a-zA-Z0-9]*' for word in words]),

            # Substring match in different words
            boundary.join(['(' + word + ').*' for word in words]),

            # Substring match anywhere (weakest, these will be the last results)
            ''.join(['(' + word + ').*' for word in words])
        ]

        # Traverse the history and build the filtered list
        self.filtered_list = []
        for pattern in patterns:
            #print '\n\n', pattern, '\n\n'
            for line in reversed(self.list):
                if line in [l for (l, p) in self.filtered_list]:
                    # We already added this line, skip
                    continue
                matches = re.search(pattern, line, re.IGNORECASE)
                if matches:
                    self.filtered_list.insert(0, (line, [matches.span(i) for i in range(1, matches.lastindex + 1)]))
                    #print '\n\n', self.filtered_list[-1], '\n\n'

        # We use the trail to navigate back in the same order
        self.trail = [(self.filter, [(0, len(self.filter))])]

    def up(self):
        """
        Navigate back in the command history
        """
        if self.filtered_list:
            self.trail.append(self.filtered_list.pop())

    def down(self):
        """
        Navigate forward in the command history
        """
        if self.trail:
            self.filtered_list.append(self.trail.pop())

    def reset(self):
        """Reset browsing through the history"""
        self.filter = ''
        self.filtered_list = []
        self.trail = []

    def add(self, line):
        """Add a new line to the history"""
        if line:
            #print 'Adding "' + line + '"'
            if line in self.list:
                self.list.remove(line)
            self.list.append(line)
            self.reset()

    def current(self):
        """Return the current history item"""
        return self.trail[-1] if self.trail else ('', [])