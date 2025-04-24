# Use the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Git, curl, and PortAudio without cleaning up
RUN apt-get update && apt-get install -y \
    git \
    curl \
    portaudio19-dev

# Install build tools (including gcc) for compiling extensions
RUN apt-get install -y build-essential

# Clone the repository from GitHub
RUN git clone https://github.com/jreivilo/lemanic_life_science_graspit.git .

# Install uv and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN mv /root/.local/bin/uv /usr/local/bin/uv

# Download leap sdk
RUN git submodule update --init --recursive

# Install ultraleap driver
RUN apt install -y wget gnupg2
RUN wget -qO - https://repo.ultraleap.com/keys/apt/gpg | gpg --dearmor | tee /etc/apt/trusted.gpg.d/ultraleap.gpg
RUN echo 'deb [arch=amd64] https://repo.ultraleap.com/apt stable main' | tee /etc/apt/sources.list.d/ultraleap.list
RUN apt update
RUN echo ultraleap-hand-tracking ultraleap-hand-tracking/eula select true | debconf-set-selections
RUN apt-get install -y ultraleap-hand-tracking

# Install Python dependencies using uv (will use uv.lock)
RUN uv sync