Feature: Test the Container
    Scenario Outline: System Under Test
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

    Scenario Outline: Python Packages
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra pip package is <pip_package>
        Then the TestInfra pip package is present

        Examples:
            | pip_package        |
            | python-qpid-proton |
            | smart_open         |
