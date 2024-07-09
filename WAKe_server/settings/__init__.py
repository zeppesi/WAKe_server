import os

ENV_SETTINGS_MODE = os.environ.get('ENV_SETTINGS_MODE')

if ENV_SETTINGS_MODE is None:
    ENV_MODE = 'local'
elif 'dev' in ENV_SETTINGS_MODE:
    ENV_MODE = 'dev'
elif 'git' in ENV_SETTINGS_MODE:
    ENV_MODE = 'git'
else:
    ENV_MODE = 'local'

if ENV_MODE == 'dev' or ENV_MODE == 'git':
    from WAKe_server.settings.dev import *
else:
    from WAKe_server.settings.local import *
