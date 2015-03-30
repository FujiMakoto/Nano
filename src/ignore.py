import logging
from database import DbSession
from database.models import IgnoreList as IgnoreListModel


class IgnoreList:
    # Valid ignore masks
    HOST = "host"
    NICK = "nick"
    validMasks = [HOST, NICK]

    def __init__(self):
        """
        Initialize a new Ignore List instance
        """
        self.log = logging.getLogger('nano.ignore')
        self.dbs = DbSession()

        # Set and synchronize our ignore list
        self._ignore_list = {'hosts': [], 'nicks': []}
        self.synchronize()

    def synchronize(self):
        """
        Synchronize the ignore list with the database entries
        """
        self.log.debug('Synchronizing ignore list entries with the database')
        # Pull our ignored hosts / nicks from the database
        hosts = self.dbs.query(IgnoreListModel.source).filter(IgnoreListModel.mask == self.HOST).all()
        nicks = self.dbs.query(IgnoreListModel.source).filter(IgnoreListModel.mask == self.NICK).all()

        # Synchronize our database entries with our active ignore list
        self._ignore_list['hosts'] = [host[0] for host in hosts]
        self._ignore_list['nicks'] = [nick[0] for nick in nicks]

    def exists(self, source):
        """
        Check if an ignore list entry for this source exists

        Args:
            source(irc.client.NickMask): The NickMask of the client being checked

        Returns:
            bool
        """
        self.log.info('Checking if "{source}" is on the client ignore list'.format(source=source))
        # Host match?
        if source.host in self._ignore_list['hosts']:
            self.log.info('Matched client to a host ignore list entry')
            return True

        # Nick match?
        if str(source.nick).lower() in self._ignore_list['nicks']:
            self.log.info('Matched client to a nick ignore list entry')
            return True

        # No match.
        return False

    def all(self):
        """
        Returns all ignore list entries in the database (Needed for ID referencing)
        """
        self.log.info('Returning all ignore list entries')
        return self.dbs.query(IgnoreListModel.id, IgnoreListModel.source, IgnoreListModel.mask).all()

    def add(self, source, mask=HOST):
        """
        Add an entry to the ignore list

        Args:
            source(str): The Nick or Host of the client to ignore
            mask(str): The ignore mask type
        """
        self.log.info('Adding "{source}" to the ignore list using the {mask} mask'.format(source=source, mask=mask))
        # Are we ignoring a host or nick mask? (Or if an invalid mask, return without doing anything)
        if mask == self.HOST:
            # Make sure this host isn't already in our ignore list
            if source in self._ignore_list['hosts']:
                raise IgnoreEntryAlreadyExistsError('An ignore list entry for this host already exists')

            # Append to our ignore list and ready our model
            self._ignore_list['hosts'].append(source)
            ignore_list_entry = IgnoreListModel(source=source, mask=mask)
        elif mask == self.NICK:
            # Make sure this nick isn't already in our ignore list
            source = str(source).lower()
            if source in self._ignore_list['nicks']:
                raise IgnoreEntryAlreadyExistsError('An ignore list entry for this nick already exists')

            # Append to our ignore list and ready our model
            self._ignore_list['nicks'].append(source)
            ignore_list_entry = IgnoreListModel(source=source, mask=mask)
        else:
            return

        # Commit to database
        self.dbs.add(ignore_list_entry)
        self.dbs.commit()

    def delete(self, source, mask=HOST):
        """
        Remove an entry from the ignore list

        Args:
            source(str): The Nick or Host of the client to remove from ignore
            mask(str): The ignore mask type

        Returns:
            bool: True if an entry was successfully removed, False if none existed
        """
        if mask == self.HOST:
            # If no ignore list entry for this host exists, return False
            if source not in self._ignore_list['hosts']:
                self.log.info(source + ' did not exist in the hosts ignore list')
                return False

            # Remove the entry from our ignore list
            self._ignore_list['hosts'].remove(source)
        elif mask == self.NICK:
            source = str(source).lower()
            # If no ignore list entry for this nick exists, return False
            if source not in self._ignore_list['nicks']:
                self.log.info(source + ' did not exist in the nicks ignore list')
                return False

            # Remove the entry from our ignore list
            self._ignore_list['nicks'].remove(source)
        else:
            self.log.warn('Invalid mask supplied when attempting to delete an ignore list entry')
            # Invalid mask, return False
            return False

        # Remove the entry from our database
        self.log.info('Removing "{source}" from the {mask} ignore list'.format(source=source, mask=mask))
        self.dbs.query(IgnoreListModel).filter(IgnoreListModel.source == source).delete()
        self.dbs.commit()
        return True

    def delete_by_id(self, db_id):
        """
        Remove an entry from the ignore list by its database ID

        Args:
            db_id(int): The database ID of the ignore list entry to delete
        """
        self.log.debug('Querying the database to delete ignore list entry ' + str(db_id))
        ignore_list_entry = self.dbs.query(IgnoreListModel.source, IgnoreListModel.mask).filter(
            IgnoreListModel.id == db_id).first()

        if not ignore_list_entry:
            self.log.info('Requested to delete a database ID entry that did not exist')
            return False

        return self.delete(ignore_list_entry[0], ignore_list_entry[1])

    def clear(self):
        """
        Clear all entries from the ignore list
        """
        self.log.info('Clearing all ignore list entries')
        # Reset the ignore list
        self._ignore_list = {'hosts': [], 'nicks': []}

        # Remove all entries from the database
        self.dbs.query(IgnoreListModel).delete()
        self.dbs.commit()


class IgnoreEntryAlreadyExistsError(Exception):
    pass