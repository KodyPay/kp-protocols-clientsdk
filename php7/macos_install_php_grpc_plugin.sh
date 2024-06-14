#!/bin/zsh

# Install Homebrew if not already installed
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew is already installed."
fi

# Install necessary tools
echo "Installing git, cmake, and protobuf..."
brew install git cmake protobuf

# Clone the gRPC repository
echo "Cloning the gRPC repository..."
git clone --recurse-submodules -b v1.41.0 https://github.com/grpc/grpc
cd grpc

# Build and install the gRPC PHP plugin
echo "Building the gRPC PHP plugin..."
mkdir -p cmake/build
cd cmake/build
cmake ../..
make grpc_php_plugin

# Move the grpc_php_plugin to a directory in the PATH
echo "Copying grpc_php_plugin to /usr/local/bin/..."
sudo cp ./grpc_php_plugin /usr/local/bin/

# Verify the installation
if command -v grpc_php_plugin &>/dev/null; then
  echo "grpc_php_plugin installed successfully!"
else
  echo "Failed to install grpc_php_plugin."
  exit 1
fi

# Verify protoc installation
if command -v protoc &>/dev/null; then
  echo "protoc installed successfully!"
  protoc --version
else
  echo "Failed to install protoc."
  exit 1
fi

# Clean up the cloned gRPC repository
echo "Cleaning up..."
cd ../../..
rm -rf grpc

echo "Installation script completed successfully and cleaned up."
