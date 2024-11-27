# File: warc_manager_app/lib/helper.py
import logging

log = logging.getLogger(__name__)


def check_collection_status(collection_id):
    """
    Checks if the collection is already downloaded or in progress.
    Dummy implementation for now.
    """
    log.debug(f'Checking status for collection ID: {collection_id}')
    # Dummy response
    return {'exists': False}  # Return True if exists or in progress


def initiate_download(collection_id):
    """
    Initiates the download for the given collection.
    Dummy implementation for now.
    """
    log.debug(f'Initiating download for collection ID: {collection_id}')
    # Dummy response
    return {'message': f'Download for collection {collection_id} started.'}


def get_collection_data(collection_id):
    """
    Gets the collection data for the given collection.
    Dummy implementation for now.
    """
    log.debug(f'Getting data for collection ID: {collection_id}')
    # Dummy response
    return {'name': 'Test Collection', 'total_size': '1.2 GB', 'item_count': 1000}
