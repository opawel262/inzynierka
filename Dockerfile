FROM python:3.12-slim-bookworm

# Ensure all system packages are up-to-date to minimize vulnerabilities
RUN apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libglib2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir -r requirements.txt

# 
COPY ./app /code/app

ENV PLOTLY_KALEIDO_EXECUTABLE="/usr/bin/chromium"
ENV PLOTLY_KALEIDO_CHROMIUM_ARGS="--no-sandbox"
ENV PYTHONPATH=/code
ENV PYTHONDONTWRITEBYTECODE=1
