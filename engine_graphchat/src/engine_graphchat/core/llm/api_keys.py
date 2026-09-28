"""
Get and store API keys

Using python keyring
"""

import logging
import getpass

import keyring


logger = logging.getLogger(__name__)
_service = "com.lsiemens.graphchat.engine"
_API_key_name = "API_key"


def clear_API_key():
    logger.info("Clear API keys.")
    try:
        keyring.delete_password(_service, _API_key_name)
    except keyring.errors.PasswordDeleteError:
        logger.exception("Failed to clear API key from keyring!")
        raise


def save_API_key(API_key):
    if API_key is None:
        raise ValueError("API key must not be None.")

    try:
        keyring.set_password(_service, _API_key_name, API_key)
    except keyring.errors.PasswordSetError:
        raise


def initialize_client(initializer):
    """Initialize a client using your API key.

    Parameters
    ----------
    initializer : function(string)
        A function that initializes a client given the API key as a string.

    Returns
    -------
    Client
        The Client initialized from `initializer` using the API key.
    """

    API_key = keyring.get_password(_service, _API_key_name)

    if API_key is None:
        print("The API key is not in your keyring.")
        while (API_key is None):
            API_key = getpass.getpass("Enter xAI API key: ")

            if len(API_key) == 0:
                print("\tThe API key can not be empty!")
                API_key = None

        try:
            save_API_key(API_key)
        except (keyring.errors.PasswordSetError, ValueError):
            logger.exception("Failed to save API key to keyring.")

    logger.info("Initialize client with API key from keyring.")
    return initializer(API_key)
