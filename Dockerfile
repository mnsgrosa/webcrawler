FROM python:3.11-slim

# Set the working directory for your application
WORKDIR /app

# Install necessary tools for downloading and unpacking
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean


# Set the Chrome version for consistency. Find recent versions on the Chrome for Testing dashboard.
ARG CHROME_VERSION="139.0.7258.68"
ARG CHROMEDRIVER_VERSION="139.0.7258.68"

RUN pip install uv

RUN apt-get update && \
    apt-get install -y google-chrome-stable

COPY pyproject.toml uv.lock* ./

RUN uv pip install --system --no-cache .

COPY ./src ./src
COPY ./scripts ./scripts
COPY ./my_dags.py ./my_dags
COPY ./page.py .