from datetime import datetime, timezone
import time


class Logger(object):
    def __init__(self):
        pass

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
        print('**')
        print('** SECURITY LOG UTC Date:', event_time)
        print('** SECURITY LOG Local   :', local_time, time.tzname)
        print('** SECURITY LOG Message : {0}'.format(text))
        print('**')
