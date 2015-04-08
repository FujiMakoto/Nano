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
        stats = commit.stats.total

        # If old_commit is None, we're already up-to-date
        if not old_commit:
            return 'Already up-to-date.'

        # Set the formatted response data
        name = '<p class="fg-orange">{name}</p>'.format(name=commit.name_rev)
        bar = self.git.commit_bar(commit)
        response = 'Updated to commit {name} - {no_files} files changed, {no_inserts} insertions(+), {no_deletes} ' \
                   'deletions(-) [{bar}]'

        return response.format(name=name, no_files=stats['files'], no_inserts=stats['insertions'],
                               no_deletes=stats['deletions'], bar=bar)

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
        Displays how many commits behind of master we are

        Args:
            command(interfaces.irc.IRCCommand): The IRC command instance
        """
        ahead, behind = self.git.status()

        # Not behind any commits
        if not behind:
            return 'Already up-to-date.'

        return 'Behind \'origin/master\' by {no_commits} commits'.format(no_commits=behind)