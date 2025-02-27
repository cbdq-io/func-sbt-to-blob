#!/usr/bin/env python
"""Extract data from a Service Bus topic and loading to blob storage."""
import datetime
import logging
import os
import sys
from urllib.parse import urlparse

import azure.functions as func
import azure.storage
import azure.storage.blob
import proton
import smart_open
from azure.core.utils import parse_connection_string
from proton import Message
from proton.utils import BlockingConnection

MAX_MESSAGES_IN_BATCH = 500


class ConnectionStringHelper:
    """
    A class for handling Azure Service Bus Connection Strings.

    Attributes
    ----------
    sbus_connection_string : str
        The value provided by the constructor.

    Parameters
    ----------
    connection_string : str
        An Azure Service Bus connection string.
    """

    def __init__(self, sbus_connection_string: str) -> None:
        self.sbus_connection_string = sbus_connection_string
        self.port(5671)
        self.protocol('amqps')
        self.parse()
        self.netloc(f'{self.protocol()}://{self.hostname()}:{self.port()}')
        url = f'{self.protocol()}://{self.key_name()}:{self.key_value()}'
        url += f'@{self.hostname()}:{self.port()}'
        self.amqp_url(url)

    def amqp_url(self, amqp_url: str = None) -> str:
        """
        Get or set an AMQP URL.

        Parameters
        ----------
        amqp_url : str, optional
            The URL to be set, by default None

        Returns
        -------
        str
            The set URL.
        """
        if amqp_url is not None:
            self._amqp_url = amqp_url
        return self._amqp_url

    def hostname(self, hostname: str = None) -> str:
        """
        Get or set the host name.

        Parameters
        ----------
        hostname : str, optional
            The host name to be set, by default None

        Returns
        -------
        str
            The set host name.
        """
        if hostname is not None:
            self._hostname = hostname
        return self._hostname

    def key_name(self, key_name: str = None) -> str:
        """
        Get or set the key name.

        Parameters
        ----------
        key_name : str
            The key name to be set.

        Returns
        -------
        str
            The key name that is set.
        """
        if key_name is not None:
            self._key_name = key_name
        return self._key_name

    def key_value(self, key_value: str = None) -> str:
        """
        Get or set the key value.

        Parameters
        ----------
        key_value : str
            The key value to be set.

        Returns
        -------
        str
            The key value that is set.
        """
        if key_value is not None:
            self._key_value = key_value
        return self._key_value

    def netloc(self, netloc: str = None) -> str:
        """
        Get or set the netloc.

        Parameters
        ----------
        netloc : str, optional
            The value to set.

        Returns
        -------
        str
            The currently set value.
        """
        if netloc is not None:
            self._netloc = netloc

        return self._netloc

    def parse(self) -> None:
        """
        Parse the connection string.

        Raises
        ------
        ValueError
            If mandatory components are missing in the connection string.
        """
        conn_str_components = dict(parse_connection_string(self.sbus_connection_string))
        use_development_emulator = conn_str_components.get('usedevelopmentemulator', 'False').capitalize()
        use_development_emulator = use_development_emulator == 'True'

        if use_development_emulator:
            self.port(5672)
            self.protocol('amqp')

        try:
            endpoint = conn_str_components['endpoint']
            url = urlparse(endpoint)
            self.hostname(url.netloc)
            self.key_name(conn_str_components['sharedaccesskeyname'])
            self.key_value(conn_str_components['sharedaccesskey'])
        except KeyError:
            raise ValueError(f'Connection string "{self.sbus_connection_string}" is invalid.')

    def port(self, port: int = None) -> int:
        """
        Get or set the port number.

        Parameters
        ----------
        port : int
            The port number to be set.

        Returns
        -------
        int
            The port number that is set.
        """
        if port is not None:
            self._port = port

        return self._port

    def protocol(self, protocol: str = None) -> str:
        """
        Get or set the protocol to be used for connecting to AMQP.

        Valid values are amqp or amqps.

        Parameters
        ----------
        protocol : str, optional
            The protocol to be used, by default None

        Returns
        -------
        str
            The protocol that has been set.
        """
        if protocol is not None:
            self._protocol = protocol

        return self._protocol


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
        self.prefix = f'azure://{self.container_name}/{self.topics_directory}/'

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
        conn_details = ConnectionStringHelper(connection_string)
        self.connection = BlockingConnection(
            url=conn_details.netloc(),
            allowed_mechs=os.getenv('ALLOWED_SASL_MECHS'),
            password=conn_details.key_value(),
            user=conn_details.key_name()
        )
        address = f'{topic_name}/Subscriptions/{subscription_name}'
        self.receiver = self.connection.create_receiver(
            address=address
        )

    def accept_messages(self, messages: list[Message]) -> None:
        """Accept the messages in the current buffer."""
        if len(messages) > 0:
            self.receiver.settle()

    def close(self) -> None:
        """Close the receiver and the connection."""
        self.receiver.close()
        self.connection.close()

    def get_messages(self) -> list[Message]:
        """
        Get messages from the topic/subscription.

        Returns
        -------
        list
            A list of messages.
        """
        messages = []

        while not self.finished:
            try:
                message = self.receiver.receive(5)
            except proton._exceptions.Timeout:
                message = None

            if message is None:
                self.finished = True
            else:
                messages.append(message)

                if len(messages) >= MAX_MESSAGES_IN_BATCH:
                    break

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

    def load(self, messages: list[Message]) -> None:
        """
        Load messages into blob storage.

        Parameters
        ----------
        messages : list[Messge]
            The messages to be loaded.
        """
        if len(messages) == 0:
            return

        last_message_in_batch = messages[-1]
        timestamp = last_message_in_batch.creation_time
        timestamp = datetime.datetime.fromtimestamp(timestamp)
        offset = last_message_in_batch.annotations['x-opt-enqueue-sequence-number']
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
                body = message.body

                if isinstance(body, memoryview):
                    body = body.tobytes().decode()
                elif isinstance(body, bytes):
                    body = body.decode()
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
    logging.basicConfig()
    logger = logging.getLogger(os.path.basename(__file__))
    logger.setLevel(os.getenv('LOG_LEVEL', 'DEBUG'))
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
    logger.info(f'Creating an extractor for {topic_name}/{subscription_name}.')
    extractor = Extractor(sbns_connection_string, topic_name, subscription_name)
    loader = Loader(
        sa_connection_string,
        container_name,
        topics_dir,
        topic_name,
        path_format
    )
    message_count = 0

    while not extractor.finished:
        messages = extractor.get_messages()
        logger.debug(f'Received {len(messages)} messages.')
        loader.load(messages)
        logger.debug(f'Loaded {len(messages)} messages to "{loader.path}".')
        logger.debug('Accepting the messages loaded...')
        extractor.accept_messages(messages)
        logger.debug('Messages accepted.')
        message_count += len(messages)
        logger.debug(f'{message_count:,} messages processed so far.')

        if extractor.finished:
            logger.debug(f'No more messages on the {topic_name} topic.')

    extractor.close()
    logger.info(f'A total of {message_count:,} messages were loaded to blob storage.')
