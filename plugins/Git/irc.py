import logging
from .plugin import GitManager


class Commands:
    """
    IRC Commands for the Git plugin
    """
    commands_help = {
        'main': [
            'Performs Git related tasks for development',
            'Available commands: <strong>pull</strong>'
        ],

        'pull': [
            'Pulls and incorporates the most recent changes from the development branch'
            'Syntax: pull'
        ],

        'current': [
            'Displays the current commit name / revision',
            'Syntax: current'
        ],

        'status': [
            'Displays how many commits behind master we are',
            'Syntax: status'
        ]
    }

    def __init__(self, plugin):
        """
        Initialize a new Git Commands instance

        Args:
            plugin(src.plugins.Plugin): The plugin instance
        """
        self.log = logging.getLogger('nano.plugins.git.irc.commands')
        self.plugin = plugin
        self.git = GitManager()

    def admin_command_pull(self, command):
        """
        Pulls and incorporates the most recent changes from the development branch
        Syntax: git pull

        Args:
            command(interfaces.irc.IRCCommand): The IRC command instance
        """
        branch, commit, old_commit = self.git.pull()

        # If old_commit is None, we're already up-to-date
        if not old_commit:
            return 'Already up-to-date.'

        # We have to manually regex parse git output because our library doesn't support diff stats
        stats_string = self.git.diff_stats(commit, old_commit)[0]

        # Set the formatted response data
        name = '<p class="fg-orange">{name}</p>'.format(name=commit.name_rev)
        bar = self.git.commit_bar(commit)
        response = 'Updated to commit {name} - {stats_string} [{bar}]'

        return response.format(name=name, stats_string=stats_string, bar=bar)

    def admin_command_current(self, command):
        """
        Displays the current commit name / revision

        Args:
            command(interfaces.irc.IRCCommand): The IRC command instance
        """
        commit = self.git.current()
        return 'Current commit: <p class="fg-orange">{name}</p>'.format(name=commit.name_rev)

    def admin_command_status(self, command):
        """
        Displays how many commits behind master we are

        Args:
            command(interfaces.irc.IRCCommand): The IRC command instance
        """
        ahead, behind = self.git.status()

        # Not behind any commits
        if not behind:
            return 'Already up-to-date.'

        return 'Behind \'origin/master\' by {no_commits} commits'.format(no_commits=behind)