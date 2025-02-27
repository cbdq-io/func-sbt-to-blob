# func-sbt-to-blob
A containerised Azure Function App to Sink data from a Service Bus Topic to
Blob Storage.

If `CONTAINER_NAME` is set to `mycontainer`, `TOPICS_DIR` is set to `topics`,
`PATH_FORMAT` is set to `year=YYYY/month=MM/day=dd/hour=HH` and
`TOPIC_NAME` is set to `mytopic`, then the file path for the data to be
loaded to will be something like:

`azure://mycontainer/topics/year=2025/month=02/day=24/hour=11/mytopic+0000000000000000042.bin.gz`

## Required Environment Variables

- `CONTAINER_NAME`: The container name within the storage account to load
  the data to.
- `SERVICE_BUS_CONNECTION_STRING`:  The connection string to connect to Azure
  Service Bus.
- `STORAGE_ACCOUNT_CONNECTION_STRING`: The connection string to connect to
  the Azure Storage Account.
- `SUBSCRIPTION_NAME`:  The name of the subscription to use to extract from
  the topic.
- `TOPIC_NAME`:  The name of the topic to extract from.

## Optional Environment Variables

- `PATH_FORMAT`: The configuration to set the format of the data directories.
  The format set in this configuration converts the timestamp of the latest
  message in the block written to proper directory strings.  Within the
  provided string the following substutions will take place:
    - `YYYY` will be replaced by the year.
    - `MM` will be replaced by the zero padded month number.
    - `dd` will be replaced by the zero padded day number.
    - `HH` will be replaced by the zero padded hour number.
    - `mm` will be replaced by the zero padded minute number.
  Default is "".
- `TOPICS_DIR`: The directory within the specified container to load the
  topics to.  Default is `topics`.

## Troubleshooting

We use the appservice base image to build on top of.  This enables the
Kudo/SSH endpoint so you can connect to the running container with the
URL:

  https://_app_name_.scm.azurewebsites.net/

Where _app_name_ is the unique name of your deployed app.  In the menu,
select SSH to connect to your running container.
