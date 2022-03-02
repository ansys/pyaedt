import logging


class LogHandler(logging.Handler):
    """Creates a handler to send log messages to the AEDT logging stream.

    Parameters
    ----------
    aedt_app_messenger : class:`pyaedt.application.MessageManager.AEDTMessageManager`
        Log manager for AEDT.
    log_destination : str
        Logger to send messages to. AEDT has three different logger options: ``"Global"``,
        ``'Project"``, and ``"Design"``.
    level : int, optional
        Threshold for this handler. For example, ``logging.DEBUG``.
    """

    def __init__(self, aedt_app_messenger, log_destination, level=logging.INFO):
        # base class's constructor must be called to set level and filters.
        logging.Handler.__init__(self, level)
        self.destination = log_destination
        self.messenger = aedt_app_messenger

    def emit(self, record):
        """Write the record to the stream.

        Parameters
        ----------
        record : class:`logging.LogRecord`
            Contains information related to the event being logged.
        """

        if record.levelname == "DEBUG":
            # Debug message does not exist for AEDT so we will log an info message.
            self.messenger.add_debug_message(self.format(record), self.destination)
        elif record.levelname == "INFO":
            self.messenger.add_info_message(self.format(record), self.destination)
        elif record.levelname == "WARNING":
            self.messenger.add_warning_message(self.format(record), self.destination)
        elif record.levelname == "ERROR" or record.levelname == "CRITICAL":
            self.messenger.add_error_message(self.format(record), self.destination)
        else:
            raise ValueError("The record level: {} is not supported.".format(record.level))
