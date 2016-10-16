from datetime import datetime, timezone
import time
import os


class Logger(object):
    _filename = "vault-demo.log"

    def __init__(self, filename=None):
        if filename is not None:
            self._filename = filename

    @staticmethod
    def log(text, security_related=False):
        if security_related:
            Logger.security_log(text)
        else:
            print('LOG: {0}'.format(text))

    @staticmethod
    def security_log(text):
        event_time = datetime.utcnow()
        local_time = event_time.replace(tzinfo=timezone.utc).astimezone(tz=None)
        output_text = \
            "**\n" + \
            "** SECURITY LOG UTC Date: {0}".format(event_time) + "\n" + \
            "** SECURITY LOG Local   :".format(local_time, time.tzname) + "\n" + \
            "** SECURITY LOG Message : {0}".format(text) + "\n" + \
            "**"
        print(output_text)
