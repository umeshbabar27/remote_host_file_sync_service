# Version of the Remote host file sync service

__version__ = '1.0.0'

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_conf_path(conf_file_name):
    print _ROOT
    return os.path.join(_ROOT, conf_file_name)
