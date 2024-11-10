#!/bin/bash

setup_venv(){
  echo "Setting up virtual environment"
  python3.10 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  source .venv/bin/activate
}


ensure_mac_brew(){
  if ! command -v brew > /dev/null; then
    echo "Homebrew is not installed. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew update
}

install_docker_mac() {
  echo "Detected macOS. Installing Docker..."
  # Check if Homebrew is installed
  ensure_mac_brew
  brew install --cask docker
  open /Applications/Docker.app && echo "Docker installed successfully"
}


install_python_mac(){
  ensure_mac_brew
  brew install python@3.10
}


install_docker_apt() {
  echo "Detected apt(ubuntu, debian). Installing Docker..."
  sudo apt update
  sudo apt install -y docker.io
  sudo systemctl start docker
  sudo systemctl enable docker && echo "Docker installed successfully"
}

install_python_apt(){
  sudo apt update
  sudo apt install -y python3.10
}

install_docker_dnf() {
  echo "Detected dnf (feedora, redhat). Installing Docker..."
  sudo dnf -y install dnf-plugins-core
  sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
  sudo dnf install -y docker-ce docker-ce-cli containerd.io
  sudo systemctl start docker
  sudo systemctl enable docker. && echo "Docker installed successfully"
}

install_python_dnf(){
  sudo dnf install -y python3.10
}


install_docker_pacman() {
  echo "Detected pacman (arch). Installing Docker..."
  sudo pacman -Syu --noconfirm
  sudo pacman -S --noconfirm docker
  sudo systemctl start docker
  sudo systemctl enable docker && echo "Docker installed successfully"
}

install_python_pacman(){
  sudo pacman -Syu --noconfirm
  sudo pacman -S --noconfirm python3.10
}


# Function to install Docker based on the OS and package manager
ensure_docker() {
  [ "$(uname)" == "Darwin" ] && install_docker_mac
  command -v apt >/dev/null 2>&1 && install_docker_apt
  command -v dnf >/dev/null 2>&1 && install_docker_dnf
  command -v pacman >/dev/null 2>&1 && install_docker_pacman
}

ensure_python(){
  [ "$(uname)" == "Darwin" ] && install_python_mac
  command -v apt >/dev/null 2>&1 && install_python_apt
  command -v dnf >/dev/null 2>&1 && install_python_dnf
  command -v pacman >/dev/null 2>&1 && install_python_pacman
}

# Check if Docker is installed and running
if [ -x "$(command -v docker)" ]; then
  echo "Docker is already installed."
  # Check if Docker daemon is running
  if ! sudo docker info > /dev/null 2>&1; then
    echo "Docker is installed but not running. Starting Docker..."
    sudo systemctl start docker || open /Applications/Docker.app
  fi
else
  echo "Docker is not installed. Attempting to install Docker..."
  ensure_docker
fi

if ! docker buildx version > /dev/null 2>&1; then
    echo "Docker buildx is not installed. Please install Docker buildx plugin."
    exit 1
fi

# check if builder instance exists
#
#
create_mybuilder(){
  echo "Creating a new builder instance..."
  sudo docker buildx create --name mybuilder --use
}

use_mybuilder(){
  echo "Using existing builder instance..."
  sudo docker buildx use mybuilder
}

activate_mybuilder(){
  echo "Activating existing builder instance..."
  sudo docker buildx inspect --bootstrap
}

# check if builder instance exists
command -v sudo dodcker buildx inspect mybuilder > /dev/null 2>&1 || create_mybuilder
# check if builder instance is active
command -v sudo docker buildx inspect mybuilder | grep -q "Status:.*inactive"  > /dev/null 2>&1 && activate_mybuilder || use_mybuilder
# check if python3.10 is installed
command -v python3.10 > /dev/null 2>&1 || ensure_python


# setup local venv and install dependencies
setup_venv
