wsgi_app = 'app:create_app()'
# chdir = '/work/python/gunic/gu'
# daemon = False
raw_env = [
    'ENV_TYPE=dev',
    'HOGEHOGE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxx'
]

bind = '0.0.0.0:8000'
workers = 1
proc_name = 'tuat-syllabus'
loglevel = 'info'