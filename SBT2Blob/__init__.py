#!/usr/bin/env python
"""Extract data from a Service Bus topic and loading to blob storage."""
import datetime
import logging
import os
import sys
import time

import azure.functions as func
import azure.storage
import azure.storage.blob
import smart_open
from azure.servicebus import (AutoLockRenewer, ServiceBusClient,
                              ServiceBusMessage)

MAX_EMPTY_RECEIVES = int(os.getenv('MAX_EMPTY_RECEIVES', '3'))
MAX_MESSAGES_IN_BATCH = int(os.getenv('MAX_MESSAGES_IN_BATCH', '500'))
MAX_RUNTIME_SECONDS = int(os.getenv('MAX_RUNTIME_SECONDS', '0'))
WAIT_TIME_SECONDS = int(os.getenv('WAIT_TIME_SECONDS', '5'))
logging.basicConfig()
logger = logging.getLogger(os.path.basename(__file__))


class LoadURI:
    """
    A class for helping with the load URI.

    Parameters
    ----------
    container_name : str
        The name of the container.
    topics_directory : str
        The name of the top-level directory in the container.
    topic_name : str
        The name of the topic to extract data from.
    path_format : str
        The path format to be appended to the topics_directory.
    """

    def __init__(self, container_name: str, topics_directory: str, topic_name: str, path_format: str):
        self.container_name = container_name
        self.topics_directory = topics_directory
        self.topic_name = topic_name
        self.path_format = path_format
        self.prefix = f'azure://{self.container_name}/{self.topics_directory}/{self.topic_name}/'

    def uri(self, offset: int, timestamp: datetime.datetime) -> str:
        """
        Generate the path for the uniform resource identifer (URI).

        Parameters
        ----------
        offset : int
            The offset of the latest message on the topic.
        timestamp : datetime.datetime
            The timestamp of the latest message on the topic.

        Returns
        -------
        str
            The URI to load the data to.
        """
        path_format = self.path_format \
            .replace('YYYY', str(timestamp.year)) \
            .replace('MM', f'{timestamp.month:02}') \
            .replace('dd', f'{timestamp.day:02}') \
            .replace('HH', f'{timestamp.hour:02}') \
            .replace('mm', f'{timestamp.minute:02}')
        uri = self.prefix + path_format + f'/{self.topic_name}+{offset:019}.bin.gz'
        return uri


class Extractor:
    """Extract data from Service Bus."""

    def __init__(self, connection_string: str, topic_name: str, subscription_name: str):
        self.finished = False
        self.client = ServiceBusClient.from_connection_string(connection_string)
        self.receiver = self.client.get_subscription_receiver(
            topic_name,
            subscription_name,
            prefetch_count=MAX_MESSAGES_IN_BATCH * 2
        )
        self.renewer = AutoLockRenewer()
        self.empty_receive_count = 0

    def accept_messages(self, messages: list[ServiceBusMessage]) -> None:
        """Accept the messages in the current buffer."""
        for message in messages:
            self.receiver.complete_message(message)

    def close(self) -> None:
        """Close the receiver and the connection."""
        self.renewer.close()
        self.receiver.close()
        self.client.close()

    def get_messages(self) -> list[ServiceBusMessage]:
        """
        Get messages from the topic/subscription.

        Returns
        -------
        list
            A list of messages.
        """
        messages = self.receiver.receive_messages(
            max_message_count=MAX_MESSAGES_IN_BATCH,
            max_wait_time=WAIT_TIME_SECONDS
        )

        # The default lock is 30 seconds.  We extend that to be auto-renewed for
        # 2 minutes.
        for message in messages:
            self.renewer.register(self.receiver, message, max_lock_renewal_duration=120)

        if len(messages) == 0:
            self.empty_receive_count += 1
            logger.debug(f'No messages received.  Empty count: {self.empty_receive_count}')
            if self.empty_receive_count >= MAX_EMPTY_RECEIVES:
                self.finished = True
        else:
            self.empty_receive_count = 0

        return messages


class Loader:
    """Load messages onto blob storage."""

    def __init__(self, connection_string: str, container_name: str, topics_dir: str, topic_name: str, path_format: str):
        self.connection_string = connection_string
        self.container_name = container_name
        self.topics_dir = topics_dir
        self.topic_name = topic_name
        self.path_format = path_format
        client = azure.storage.blob.BlobServiceClient.from_connection_string(self.connection_string)
        self.transport_params = {
            'client': client
        }
        self.path = None

    def load(self, messages: list[ServiceBusMessage]) -> None:
        """
        Load messages into blob storage.

        Parameters
        ----------
        messages : list[ServiceBusMessage]
            The messages to be loaded.
        """
        if len(messages) == 0:
            return

        first_message_in_batch = messages[-1]
        timestamp = first_message_in_batch.enqueued_time_utc
        offset = first_message_in_batch.sequence_number
        uri = LoadURI(
            container_name=self.container_name,
            topics_directory=self.topics_dir,
            topic_name=self.topic_name,
            path_format=self.path_format
        )
        uri = uri.uri(offset=offset, timestamp=timestamp)
        self.path = uri

        with smart_open.open(uri, 'w', transport_params=self.transport_params) as stream:
            for message in messages:
                body = str(message)
                stream.write(body + '\n')


def get_environment_variable(key_name: str, default=None, required=False) -> str:
    """
    Get and environment variable value.

    Parameters
    ----------
    key_name : str
        The name of the environment variable.
    default : str
        The value to set if key_name is not set and required is false.
    required : bool, optional
        If set to true and the variable is not set, exit with error.
        Default is false.

    Returns
    -------
    str
        The value of the environment variable.
    """
    value = os.getenv(key_name)

    if required and value is None:
        logging.error(f'Missing required environment variable "{key_name}".')
        sys.exit(2)
    elif value is None and default is not None:
        value = default

    return value


def main(timer: func.TimerRequest) -> None:
    """Control the main processing."""
    log_level = os.getenv('LOG_LEVEL', 'WARN')
    logger.setLevel(log_level)
    logger.debug(f'Log level is {logging.getLevelName(logger.getEffectiveLevel())}.')

    if timer.past_due:
        logger.warning('The timer is past due!')

    container_name = get_environment_variable('CONTAINER_NAME', required=True)
    path_format = get_environment_variable('PATH_FORMAT', default='')
    sa_connection_string = get_environment_variable('STORAGE_ACCOUNT_CONNECTION_STRING', required=True)
    sbns_connection_string = get_environment_variable('SERVICE_BUS_CONNECTION_STRING', required=True)
    subscription_name = get_environment_variable('SUBSCRIPTION_NAME', required=True)
    topics_dir = get_environment_variable('TOPICS_DIR', default='topics')
    topic_name = get_environment_variable('TOPIC_NAME', required=True)
    extractor = Extractor(sbns_connection_string, topic_name, subscription_name)
    loader = Loader(
        sa_connection_string,
        container_name,
        topics_dir,
        topic_name,
        path_format
    )
    message_count = 0
    start_time = time.monotonic()

    while not extractor.finished:
        if MAX_RUNTIME_SECONDS and (time.monotonic() - start_time >= MAX_RUNTIME_SECONDS):
            logger.warning(
                f'Max runtime of {MAX_RUNTIME_SECONDS} seconds exceeded for {topic_name}. '
                f'Breaking early.'
            )
            break

        messages = extractor.get_messages()
        loader.load(messages)
        extractor.accept_messages(messages)
        message_count += len(messages)

    extractor.close()
    logger.info(f'A total of {message_count:,} messages were loaded to blob storage for {topic_name}.')
