# Changelog


## 0.5.1 (2025-09-05)

### Fix

* Correct dead-letter identification. [Ben Dalling]


## 0.5.0 (2025-09-05)

### Features

* Add Prometheus endpoint to the multi-topic entrypoint. [Ben Dalling]

* Optionally check for the existence of dead-letter messages. [Ben Dalling]

* Copy the nukedlq.py script from the sbus-router container. [Ben Dalling]

### Build

* Release/0.5.0. [Ben Dalling]

* Update allowed vulnerabilities. [Ben Dalling]

* Microsoft seem to have dropped support for arm64 images. [Ben Dalling]


## 0.4.0 (2025-07-30)

### Features

* Add the MAX_RUNTIME_SECONDS option. [Ben Dalling]

### Fix

* Configure PYTHONPATH in the container. [Ben Dalling]

### Build

* Release/0.4.0. [Ben Dalling]

* Add to allowed vulnerabilities list. [Ben Dalling]

### Continuous Integration

* Ensure emulator credentials are available for testing. [Ben Dalling]

* Show SUT logs. [Ben Dalling]


## 0.3.0 (2025-06-12)

### Features

* Add alternative entrypoint. [James Loughlin]

### Fix

* Allow CVE-2025-4673. [Ben Dalling]

* Allow CVE-2024-45336, CVE-2024-45341, CVE-2025-22866 and CVE-2025-22871. [Ben Dalling]

* Resolve CVE-2025-4598. [Ben Dalling]

### Build

* Release/0.3.0. [James Loughlin]

* Migrate to a containerised change log generator. [Ben Dalling]

### Continuous Integration

* Add a periodic Trivy scan. [Ben Dalling]

### Tests

* Ensure the alternative entrypoint is available in the container. [Ben Dalling]


## 0.2.1 (2025-04-09)

### Fix

* Tidy up the files on the image. [Ben Dalling]

* Make the method of extracting messages from Service Bus more robust. [Ben Dalling]


## 0.2.0 (2025-03-26)

### Features

* Add options to set MAX_MESSAGES_IN_BATCH and WAIT_TIME_SECONDS. [Ben Dalling]

### Fix

* Correct the implementation of the load path. BREAKING CHANGE:  This changes the format of the file path in the blob storage. [Ben Dalling]


## 0.1.0 (2025-03-05)

### Features

* Initial prototype. [Ben Dalling]

### Fix

* Auto-renew the message lock for two minutes. [Ben Dalling]

* Migrate from Qpid Proton to Azure Service Bus SDK. [Ben Dalling]

* Switch to the appservice base image. [Ben Dalling]

* Add required files and refactor the directory layout in the image. [Ben Dalling]

### Continuous Integration

* Add GitHub workflows for CI/CD. [Ben Dalling]


