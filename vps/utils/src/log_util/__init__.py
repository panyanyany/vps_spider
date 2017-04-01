import logging
import types
import collections
import yaml
import logging.handlers
import logging.config
import os
import io

THIS_DIR = os.path.dirname(__file__)



class MyAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'connid' key, whose value in brackets is prepended to the log message.
    """
    def process(self, msg, kwargs):
        msg = msg.replace('\n', '\n'+' '*4)
        return msg, kwargs


class ContextFilter(logging.Filter):
    """
    [doc](https://docs.python.org/2/howto/logging-cookbook.html#using-filters-to-impart-contextual-information)
    """
    LVLNAMES = {
        logging.DEBUG: 'DBG',
        logging.INFO: 'INF',
        logging.WARNING: 'WRN',
        logging.ERROR: 'ERR',
        logging.CRITICAL: 'CRT',
    }

    def filter(self, record):

        record.lvlname = self.LVLNAMES[record.levelno]
        # record.message = record.message.replace('\n', '\n' + ' '*4)
        return True


def SetWriteMethod(self):
    def write(self, s):
        repl = '\n'+' '*4
        s = s.replace('\n', repl)
        if s.endswith(repl):
            s = s[:-4]
        return self.write.origin_write(s)

    setattr(write, 'origin_write', self.write)
    bound_method = types.MethodType(write, self)
    setattr(self, 'write', bound_method)
    return


class IndentDi(object):
    def emit(self, record):
        try:
            if not hasattr(self.stream.write, 'origin_write'):
                SetWriteMethod(self.stream)
            super().emit(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class ConsoleHandler(IndentDi, logging.StreamHandler): pass


class TimedRotatingFileHandler(IndentDi, logging.handlers.TimedRotatingFileHandler): pass


class DebugRotatingFileHandler(IndentDi, logging.handlers.BaseRotatingHandler): 
    """
    Handler for logging to a set of files, which switches from one file
    to the next when the current file reaches a certain size.
    """
    def __init__(self, filename, mode='a', backupCount=0, encoding=None, delay=False):
        """
        Open the specified file and use it as the stream for logging.

        By default, the file grows indefinitely. You can specify particular
        values of maxBytes and backupCount to allow the file to rollover at
        a predetermined size.

        Rollover occurs whenever the current log file is nearly maxBytes in
        length. If backupCount is >= 1, the system will successively create
        new files with the same pathname as the base file, but with extensions
        ".1", ".2" etc. appended to it. For example, with a backupCount of 5
        and a base file name of "app.log", you would get "app.log",
        "app.log.1", "app.log.2", ... through to "app.log.5". The file being
        written to is always "app.log" - when it gets filled up, it is closed
        and renamed to "app.log.1", and if files "app.log.1", "app.log.2" etc.
        exist, then they are renamed to "app.log.2", "app.log.3" etc.
        respectively.

        If maxBytes is zero, rollover never occurs.
        """
        # If rotation/rollover is wanted, it doesn't make sense to use another
        # mode. If for example 'w' were specified, then if there were multiple
        # runs of the calling application, the logs from previous runs would be
        # lost if the 'w' is respected, because the log file would be truncated
        # on each run.
        super().__init__(filename, mode, encoding, delay)
        self.backupCount = backupCount
        self.pid = None # os.getpid()

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                dfn = self.rotation_filename("%s.%d" % (self.baseFilename,
                                                        i + 1))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(self.baseFilename + ".1")
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """
        if not self.pid:
            self.pid = os.getpid()
            return 1
        return 0
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0



### setup logging
def setup():
    logCfgFilePath = os.path.join(THIS_DIR, 'logging.yml')
    with open(logCfgFilePath) as fp:
        config = yaml.safe_load(fp.read())

    logging.config.dictConfig(config)
    # besides `LOG_ENABLE = False` in settings.py, another way to disable default Handler of scrapy
    # make sure scrapy could not set root handler in runtime
    # logging.root.addHandler = lambda e: e
