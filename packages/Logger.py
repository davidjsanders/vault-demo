from datetime import datetime, timezone
import time
import os


class Logger(object):
    _filename = "vault-demo.log"
    _log_directory = "/var/log/"

    def __init__(self, filename=None, log_directory=None):
        if filename is not None:
            self._filename = filename
        if log_directory is not None:
            self._log_directory = log_directory

    def log(self, text, security_related=False):
        if security_related:
            self.security_log(text)
        else:
            output_text = 'LOG: {0}'.format(text)
            print(output_text)
            self._file_writer(output_text)

    def security_log(self, text):
        event_time = datetime.utcnow()
        local_time = event_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
        output_text = \
            "**\n" + \
            "** SECURITY LOG UTC Date: {0}".format(event_time) + "\n" + \
            "** SECURITY LOG Local   :".format(local_time, time.tzname) + "\n" + \
            "** SECURITY LOG Message : {0}".format(text) + "\n" + \
            "**"
        print(output_text)
        self._file_writer(output_text)

    def _file_writer(self, text=None):
        try:
            f = open(Logger._log_directory + '/' + self._filename, 'a')
            f.write(text)
        except:
            pass
        finally:
            if f is not None:
                f.close()
