FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# Install system dependencies for GTK and Python bindings
RUN apt-get update && apt-get install -y \
    cmake \
    pkg-config \
    libgirepository1.0-dev \
    libcairo2-dev \
    libgtk-3-dev \
    libgtk-3-0 \
    gir1.2-gtk-3.0 \
    python3-dev \
    python3-gi \
    libdbus-1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install briefcase using pip
RUN pip install --upgrade pip
RUN pip install briefcase