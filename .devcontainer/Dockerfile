FROM mcr.microsoft.com/vscode/devcontainers/python:0-3.9

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade ciso8601 colorlog black pylint pytest pytest-cov aiohttp pytest-asyncio myfitnesspal
RUN python -m pip install --upgrade git+git://github.com/home-assistant/home-assistant.git@dev
RUN cd && mkdir -p /config/custom_components


WORKDIR /workspace

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash