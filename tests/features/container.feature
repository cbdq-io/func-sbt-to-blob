Feature: Test the Container
    Scenario: System Under Test
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra file is /home/app/function_app.py
        Then the TestInfra file is present
        And the TestInfra file type is file
        And the TestInfra file owner is app
        And the TestInfra file group is app
        And the TestInfra file mode is 0o755

    Scenario Outline: Python Packages
        Given the TestInfra host with URL "docker://sut" is ready
        When the TestInfra pip package is <pip_package>
        Then the TestInfra pip package is present

        Examples:
            | pip_package        |
            | python-qpid-proton |
            | smart_open         |
