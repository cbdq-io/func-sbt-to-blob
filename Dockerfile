FROM mcr.microsoft.com/azure-functions/python:4-python3.12-appservice

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY --chown=app:app --chmod=644 constraints.txt /home/app/constraints.txt
COPY --chown=app:app --chmod=644 requirements.txt /home/app/requirements.txt
COPY --chown=app:app --chmod=755 multi-topic-entrypoint.py /usr/local/bin/multi-topic-entrypoint.py

RUN apt-get update \
  && apt-get upgrade --yes libsystemd0 libudev1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --constraint /home/app/constraints.txt --no-cache-dir --requirement /home/app/requirements.txt

ENV PYTHONPATH="/home/site/wwwroot"
COPY --chown=app:app . /home/site/wwwroot
