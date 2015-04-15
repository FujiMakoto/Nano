import logging
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


class Scheduler:
    """
    IRC background task scheduler
    """
    def __init__(self, irc):
        """
        Initialize a new IRC Background Scheduler instance

        Args:
            irc(interfaces.irc.nano_irc.NanoIRC)
        """
        self.log = logging.getLogger('nano.irc.scheduler')
        self.irc = irc

        # Set up the scheduler tasks
        scheduler.add_job(self.flush_logs, 'interval', id='flush_logs', minutes=1)
        scheduler.start()

    def flush_logs(self):
        """
        Flush the IRC Channel and Query logfiles to disk every minute
        """
        self.log.info('Flushing channel and query logfiles')
        self.irc.channel_logger.flush()

        for nick, logger in self.irc.query_loggers.items():
            logger.flush()