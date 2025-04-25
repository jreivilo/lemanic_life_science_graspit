#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

error_exit() {
  echo -e "${RED}[ERROR] $1${NC}"
  exit 1
}
info() {
  echo -e "${YELLOW}[INFO] $1${NC}"
}
success() {
  echo -e "${GREEN}[OK] $1${NC}"
}
prefix_output() {
  local prefix=$1
  sed -u "s/^/[$prefix] /"
}
cleanup() {
  echo -e "${RED}\n[INFO] Caught interrupt. Cleaning up...${NC}"
  kill $SENSOR_PID $COMMANDER_PID $STIMULATOR_PID $MOSQUITTO_PID 2>/dev/null
  kill $(jobs -p) 2>/dev/null
  exit 1
}
trap cleanup SIGINT

# Check LEAP
if ! command -v leapctl >/dev/null 2>&1; then
    info "Leap Motion not found. Installing..."
    wget -qO - https://repo.ultraleap.com/keys/apt/gpg | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/ultraleap.gpg
    echo 'deb [arch=amd64] https://repo.ultraleap.com/apt stable main' | sudo tee /etc/apt/sources.list.d/ultraleap.list
    sudo apt update
    sudo apt install ultraleap-hand-tracking
    success "leapctl is installed."
fi

# Check UV
if ! command -v uv >/dev/null 2>&1; then
    info "Make sure curl is installed..."
    if ! command -v curl >/dev/null 2>&1; then
        info "curl not found. Installing..."
        sudo apt update
        sudo apt install curl
        success "curl installed."
    fi
    info "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    success "uv is installed."
fi

# Check if submodules are initialized
if [ ! -d "infrared-camera-sdk" ]; then
    info "Submodules not initialized. Initializing..."
    git submodule update --init --recursive || error_exit "Failed to initialize submodules."
    success "Submodules initialized."
fi

# Install Python packages
info "Syncing python packages with uv (will download if missing)..."
uv sync || error_exit "Failed to synchronize Python packages."

# Check and run MQTT broker 
if ! command -v mosquitto >/dev/null 2>&1; then
    info "Mosquitto not found. Installing..."
    
    # If using brew (we suppose MacOS)
    if command -v brew >/dev/null 2>&1; then
        info "Installing Mosquitto using Homebrew..."
        brew install mosquitto || error_exit "Failed to install Mosquitto."
    else # We assume linux
        sudo apt update
        sudo apt install mosquitto || error_exit "Failed to install Mosquitto."
    fi
    
    success "Mosquitto installed."
fi

info "Starting MQTT broker..."
mosquitto 2>&1 | prefix_output "mosquitto" &
MOSQUITTO_PID=$!

# Set default MQTT hostname
export MQTT_HOSTNAME=${MQTT_HOSTNAME:-localhost}
info "MQTT_HOSTNAME set to: $MQTT_HOSTNAME"

# Run the 3 nodes in parallel
info "Starting sensor, commander, and stimulator nodes..."

uv run src/llsg/sensor/sensor.py 2>&1 | prefix_output "sensor" &
SENSOR_PID=$!

uv run src/llsg/commander/commander.py 2>&1 | prefix_output "commander" &
COMMANDER_PID=$!

uv run src/llsg/stimulator/stimulator.py 2>&1 | prefix_output "stimulator" &
STIMULATOR_PID=$!

success "All nodes running. System initialized."

# Wait for all background jobs
while true; do
  wait -n || break
done
