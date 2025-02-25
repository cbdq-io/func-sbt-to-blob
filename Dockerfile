FROM mcr.microsoft.com/azure-functions/python:4-python3.12

COPY --chown=app:app --chmod=644 constraints.txt /home/app/constraints.txt
COPY --chown=app:app --chmod=644 requirements.txt /home/app/requirements.txt

# hadolint ignore=DL3008
RUN apt-get update \
  && apt-get install --no-install-recommends --yes gcc libc-dev \
  && pip install --constraint /home/app/constraints.txt --no-cache-dir --requirement /home/app/requirements.txt \
  && apt-get purge --yes gcc libc-dev \
  && apt-get autoremove --yes \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=app:app --chmod=755 function_app.py /home/app/function_app.py
