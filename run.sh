#!/bin/bash


install_docker_mac() {
  echo "Detected macOS. Installing Docker..."
  # Check if Homebrew is installed
  command -v brew >/dev/null 2>&1 || { echo >&2 "Homebrew is not installed. Installing Homebrew..."; /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; }
  brew update
  brew install --cask docker
  open /Applications/Docker.app && echo "Docker installed successfully"
}

install_docker_apt() {
  echo "Detected apt(ubuntu, debian). Installing Docker..."
  sudo apt update
  sudo apt install -y docker.io
  sudo systemctl start docker
  sudo systemctl enable docker && echo "Docker installed successfully"
}

install_docker_dnf() {
  echo "Detected dnf (feedora, redhat). Installing Docker..."
  sudo dnf -y install dnf-plugins-core
  sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
  sudo dnf install -y docker-ce docker-ce-cli containerd.io
  sudo systemctl start docker
  sudo systemctl enable docker. && echo "Docker installed successfully"
}


install_docker_pacman() {
  echo "Detected pacman (arch). Installing Docker..."
  sudo pacman -Syu --noconfirm
  sudo pacman -S --noconfirm docker
  sudo systemctl start docker
  sudo systemctl enable docker && echo "Docker installed successfully"
}


# Function to install Docker based on the OS and package manager
install_docker() {
  [ "$(uname)" == "Darwin" ] && install_docker_mac
  command -v apt >/dev/null 2>&1 && install_docker_apt
  command -v dnf >/dev/null 2>&1 && install_docker_dnf
  command -v pacman >/dev/null 2>&1 && install_docker_pacman
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
  install_docker
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t buddy-matcher .

# Run the Docker container
echo "Running Docker container..."
docker run --rm -it buddy-matcher
