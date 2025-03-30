import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app import celery

if __name__ == '__main__':
    celery.worker_main(argv=['worker', '-B', '--pool=solo', '-E', '--loglevel=info'])
