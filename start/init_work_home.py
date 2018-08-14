import os
import sys


def init():
    work_home = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # print('init: ' + work_home)
    sys.path.append(work_home)
    return work_home
