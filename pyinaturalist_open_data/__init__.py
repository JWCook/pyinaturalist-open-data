# flake8: noqa: F401
__version__ = '0.1.0'

try:
    from .database import load_all
    from .download import download_metadata
    from .models import *

# Ignore ImportErrors, if this is imported outside a virtualenv at build time
except ImportError as e:
    print(e)
