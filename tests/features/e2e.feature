@system
Feature: End to End Tests

    Place messages onto a topic and ensure they're loaded onto
    blob storage.

Scenario: Entry Criteria
    Given the Azurite Blob Connection String
    And the Service Bus Emulator Connection String
    When the Azurite Blob Service Client is Created
    Then create the container
    And produce the messages to the topic
    And run the function

Scenario: Exit Criteria
    Given the Azurite Blob Connection String
    When the Azurite Blob Service Client is Created
    Then the blob count should be 2
    And the earliest file should contain 500 messages
    And the latest file should contain 12 messages
