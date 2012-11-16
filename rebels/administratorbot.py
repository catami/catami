"""A bot to check database integrity and manage backups
"""

__author__ = "Dan Marrable"

import logging
from django.db import connections
from django.db.utils import ConnectionDoesNotExist
logger = logging.getLogger(__name__)

def check_database_connection(dbname='Force'):
    """Check to see if database connection is open. Return True or False

    The return is true if connection is open false if connection failed
    """

    try:
        cursor = connections[dbname].cursor()

        if cursor:
            logger.debug('Connection open to database :: ' + dbname)
            return True

    except ConnectionDoesNotExist:
        logger.debug('!! Cannot connect to database :: ' +
                     dbname + ' :: Query failed')
        return False
