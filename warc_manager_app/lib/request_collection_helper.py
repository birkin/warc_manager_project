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


def get_recent_collections() -> list:
    """
    Shows the recent collections.
    Dummy implementation for now.
    """
    log.debug('Showing recent collections')
    # Dummy response
    dummy_data = [
        {
            'date': '2024-09-01',
            'collection_id': 1,
            'title': 'Test Collection 1',
            'number_of_items': 25,
            'total_size': '100 MB',
            'status': 'complete',
        },
        {
            'date': '2024-09-02',
            'collection_id': 2,
            'title': 'Test Collection 2',
            'number_of_items': 50,
            'total_size': '200 MB',
            'status': 'in-progress',
        },
        {
            'date': '2024-09-03',
            'collection_id': 3,
            'title': 'Test Collection 3',
            'number_of_items': 75,
            'total_size': '150 MB',
            'status': 'complete',
        },
        {
            'date': '2024-09-04',
            'collection_id': 4,
            'title': 'Test Collection 4',
            'number_of_items': 100,
            'total_size': '2.1 GB',
            'status': 'in-progress',
        },
        {
            'date': '2024-09-01',
            'collection_id': 5,
            'title': 'Test Collection 5',
            'number_of_items': 125,
            'total_size': '300 MB',
            'status': 'complete',
        },
    ]
    # sort dict by date descending
    dummy_data.sort(key=lambda x: x['date'], reverse=True)
    return dummy_data


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
