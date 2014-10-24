import re
import time

from nailgun.api.v1.handlers.logs import read_log
from nailgun.settings import settings


def test_astute_performance():
    log_file = 'astute.log'
    log_config = [log for log in settings.LOGS if log['id'] == 'astute'][0]

    max_entries = 100000
    regexp = re.compile(log_config['regexp'])

    read_log(
        log_file,
        log_config=log_config,
        max_entries=max_entries,
        regexp=regexp
    )


if __name__ == '__main__':
    start = time.time()
    test_astute_performance()
    print time.time() - start