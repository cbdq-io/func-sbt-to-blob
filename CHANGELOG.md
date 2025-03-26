# Changelog


## Unreleased

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


