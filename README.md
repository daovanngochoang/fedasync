# Federated Learning Project

## Setup Development Environment
### Install docker on linux
1. Install docker For Debian/Ubuntu or Debian-based

```bash

# update and install necessary tools
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# add key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install docker 
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
``` 

2. Enable using docker without sudo 

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```
now you can use docker without sudo right
### Install RabbitMQ in docker.

simply run: 

```bash
docker run --rm -it --name rabbitmq -p 15672:15672 -p 5672:5672 rabbitmq:3-management 
```



