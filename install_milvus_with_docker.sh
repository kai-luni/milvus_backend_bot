#!/bin/bash

# Update package list and install docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io ca-certificates curl gnupg python3-pip

# Create directory for keyrings and set appropriate permissions
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add docker repository to apt sources list
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package list again and install docker and plugins
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Change to home directory
cd ~/

# Download Milvus standalone docker-compose file
wget https://github.com/milvus-io/milvus/releases/download/v2.2.5/milvus-standalone-docker-compose.yml -O docker-compose.yml

# Install docker compose plugin
sudo apt-get install -y docker-compose

# Run docker compose
sudo docker-compose up -d

echo "You should see 3 Docker container"
sudo docker ps

