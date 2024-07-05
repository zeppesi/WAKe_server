import os

ENV_SETTINGS_MODE = os.environ.get('ENV_SETTINGS_MODE')

if ENV_SETTINGS_MODE is None:
    ENV_MODE = 'local'
elif 'dev' in ENV_SETTINGS_MODE:
    ENV_MODE = 'dev'
else:
    ENV_MODE = 'local'

if ENV_MODE == 'dev':
    from WAKe_server.settings.dev import *
else:
    from WAKe_server.settings.local import *
