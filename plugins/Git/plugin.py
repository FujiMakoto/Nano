import os
import re
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

        # Regex parsing
        self.re_files_changed = re.compile('(\d+?) files? changed')
        self.re_insertions = re.compile('(\d+) insertions?')
        self.re_deletions = re.compile('(\d+?) deletions?')

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

    def diff_stats(self, commit1, commit2):
        """
        Return the formatted diff stat string, file changes, insertions and deletions for two commits

        Args:
            commit1(git.Commit): The first Commit to diff
            commit2(git.Commit): The second Commit to diff

        Returns
            tuple (0: stats_string(str), 1: files_changed(int), 2: insertions(int), 3: deletions(int))
        """
        # Defaults
        files_changed = 0
        insertions = 0
        deletions = 0

        # Get our stats string and parse the attributes
        stats_sting = self.repo.git.diff('--shortstat', commit1.hexsha, commit2.hexsha)
        if not stats_sting:
            return '', files_changed, insertions, deletions
        stats_sting = stats_sting.strip()

        # Files changed
        files_changed_match = self.re_files_changed.search(stats_sting)
        if files_changed_match:
            try:
                files_changed = int(files_changed_match.group(1))
            except ValueError as e:
                self.log.warn('Exception thrown when trying to set files_changed', exc_info=e)

        # Insertions
        insertions_match = self.re_insertions.search(stats_sting)
        if insertions_match:
            try:
                insertions = int(insertions_match.group(1))
            except ValueError as e:
                self.log.warn('Exception thrown when trying to set insertions', exc_info=e)

        # Deletions
        deletions_match = self.re_deletions.search(stats_sting)
        if deletions_match:
            try:
                deletions = int(deletions_match.group(1))
            except ValueError as e:
                self.log.warn('Exception thrown when trying to set insertions', exc_info=e)

        return stats_sting, files_changed, insertions, deletions

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