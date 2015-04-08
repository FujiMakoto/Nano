import os
import logging
from git import Repo


class GitManager:
    """
    Git plugin for development
    """
    def __init__(self):
        """
        Initialize a new Git Manager instance
        """
        self.log = logging.getLogger('nano.plugins.git')
        # Set our repo and origin branch
        self.repo = Repo(os.getcwd())
        self.origin = self.repo.remotes['origin']

    def pull(self):
        """
        Pull our latest commit and return some basic fetch information on the master branch

        Returns:
            tuple (name(str), commit(git.Commit), old_commit(git.Commit or None))
        """
        self.log.info('Pulling the most recent commit')
        fetch_info = self.origin.pull().pop(0)
        return fetch_info.name, fetch_info.commit, fetch_info.old_commit

    def current(self):
        """
        Fetch the current commit

        Returns:
            git.Commit
        """
        self.log.info('Fetching the current commit')
        return self.origin.refs.master.commit

    def status(self):
        """
        Returns how many commits ahead / behind we are

        Returns:
            list [0: ahead(int), 1: behind(int)]
        """
        self.log.info('Determining how many commits ahead / behind the remote repository we are')
        ahead, behind = self.repo.git.rev_list('--count', '--left-right', 'master...origin/master').split('\t')

        # How many commits ahead?
        try:
            ahead = int(ahead)
        except ValueError:
            ahead = 0

        # How many commits behind?
        try:
            behind = int(behind)
        except ValueError:
            behind = 0

        return ahead, behind

    @staticmethod
    def commit_bar(commit, max_length=16, color=True):
        """
        Formats and returns an insertion / deletions bar for a given commit

        Args:
            commit(git.Commit): The Git Commit instance
            max_length(int, optional): The maximum length of the commit bar. Defaults to 16
            color(bool): Apply HTML color formatting to the pluses and minuses

        Returns:
            str
        """
        insertions = int(commit.stats.total['insertions'])
        deletions = int(commit.stats.total['deletions'])
        total = insertions + deletions

        # Bar formatting
        def bar(inserts, deletes):
            # Set the pluses and minuses
            pluses  = '+' * inserts
            minuses = '-' * deletes

            # HTML color formatted response
            if color:
                # Dynamically add pluses and minuses so we don't end up with empty format strings
                bar_string = ''
                if pluses:
                    bar_string += '<p class="fg-green">{pluses}</p>'
                if minuses:
                    bar_string += '<p class="fg-red">{minuses}</p>'

                return bar_string.format(pluses=pluses, minuses=minuses)

            # Unformatted response
            return pluses + minuses

        # If our total is less than our limit, we don't need to do anything further
        if total <= max_length:
            return bar(insertions, deletions)

        # Otherwise, trim the insertions / deletions to adhere to the max length
        percent_insertions = insertions / total
        insertions = round(total * percent_insertions)
        deletions = abs(total - insertions)

        return bar(insertions, deletions)