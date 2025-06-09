# Changelog


## Unreleased

### Other

* Ci: add a periodic Trivy scan. [Ben Dalling]


## 0.2.1 (2025-04-09)

### Fix

* Tidy up the files on the image. [Ben Dalling]

* Make the method of extracting messages from Service Bus more robust. [Ben Dalling]


## 0.2.0 (2025-03-26)

### Fix

* Correct the implementation of the load path. BREAKING CHANGE:  This changes the format of the file path in the blob storage. [Ben Dalling]

### Features

* Add options to set MAX_MESSAGES_IN_BATCH and WAIT_TIME_SECONDS. [Ben Dalling]


## 0.1.0 (2025-03-05)

### Fix

* Auto-renew the message lock for two minutes. [Ben Dalling]

* Migrate from Qpid Proton to Azure Service Bus SDK. [Ben Dalling]

* Switch to the appservice base image. [Ben Dalling]

* Add required files and refactor the directory layout in the image. [Ben Dalling]

### Features

* Initial prototype. [Ben Dalling]

### Other

* Ci: Add GitHub workflows for CI/CD. [Ben Dalling]


