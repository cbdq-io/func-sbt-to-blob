#!/usr/bin/env python
"""A shim for the ghcr.io/cbdq-io/func-sbt-to-blob image to run multiple topics."""
import os
import signal

import SBT2Blob


class MockTimer:
    """A mock azure.functions.TimerRequest."""

    def __init__(self):
        self.past_due = False


class Archivist:
    """
    A class for archiving multiple topics and subscriptions.

    Parameters
    ----------
    topics_and_subscriptions : str
        A string of comma separated values that are themselves colon
        separated values for topic and subscription.
    """

    def __init__(self, topics_and_subscriptions: str = os.getenv('TOPICS_AND_SUBSCRIPTIONS', '')) -> None:
        self._topics_and_subscriptions = []
        self._is_running = True
        self.topics_and_subscriptions(topics_and_subscriptions)
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def run(self) -> None:
        """Run the class until a signal is received."""
        while self._is_running:
            for (topic_name, subscription_name) in self.topics_and_subscriptions():
                os.environ['TOPIC_NAME'] = topic_name
                os.environ['SUBSCRIPTION_NAME'] = subscription_name
                SBT2Blob.main(MockTimer())

    def stop(self, signum, frame) -> None:
        """Handle a signal if received to initiate a stop."""
        self._is_running = False

    def topics_and_subscriptions(self, topics_and_subscriptions: str = None) -> list[tuple]:
        """
        Get or set the topics and subscriptions.

        Parameters
        ----------
        topics_and_subscriptions : str, optional
            A string of comma separated values that are themselves colon
            separated values for topic and subscription, by default None

        Returns
        -------
        list[tuple]
            A list of tuples where the fist element is the topic name and the
            second element is the name of the subscription.
        """
        if topics_and_subscriptions is not None:
            self._topics_and_subscriptions = []
            items = topics_and_subscriptions.split(',')

            for item in items:
                self._topics_and_subscriptions.append(tuple(item.split(':')))

        return self._topics_and_subscriptions


if __name__ == '__main__':
    widget = Archivist()
    widget.run()
