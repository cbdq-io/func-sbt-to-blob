Feature: Test the Container
    Scenario Outline: Present Files Owner By the App User
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra file is <path>
        Then the TestInfra file is present
        And the TestInfra file type is file
        And the TestInfra file owner is app
        And the TestInfra file group is app

        Examples:
            | path                                      |
            | /home/site/wwwroot/host.json              |
            | /home/site/wwwroot/SBT2Blob/__init__.py   |
            | /home/site/wwwroot/SBT2Blob/function.json |
            | /usr/local/bin/multi-topic-entrypoint.py  |

    Scenario Outline: Absent Files
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra file is <path>
        Then the TestInfra file is absent

        Examples:
            | path                                    |
            | /home/site/wwwroot/CHANGELOG.md         |
            | /home/site/wwwroot/LICENSE              |
            | /home/site/wwwroot/requirements-dev.txt |

    Scenario Outline: Python Packages
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra pip package is <pip_package>
        Then the TestInfra pip package is present

        Examples:
            | pip_package      |
            | azure-servicebus |
            | smart_open       |
