from fabric import Connection
from invoke import Responder
from fabric import task
from patchwork.files import append
import json
import uuid

import os
import logging

logging.raiseExceptions=False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from config import (NEW_PASSWORD,
                    NEW_USERNAME,
                    NEW_HOSTNAME,
                    ORIGINAL_HOSTNAME,
                    ORIGINAL_PASSWORD,
                    ORIGINAL_USERNAME,
                    ACCESS_IP,
                    CERTS_NAME,
                    TUNNEL_CERTS_NAME
                    )
