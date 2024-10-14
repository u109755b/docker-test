# how to use in AWS EC2
# sudo yum install git -y
# git clone https://github.com/u109755b/docker-test.git
# bash docker-test/setup.sh


# git install
sudo yum install git

# docker install
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
docker --version

# ec2-userをdockerグループに入れることでdockerデーモンに接続する権限をあげる
sudo usermod -aG docker ec2-user
newgrp docker
docker ps

# docker-compose install
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# python version upgrade to 3.9.7
sudo yum groupinstall "Development Tools" -y
sudo yum install gcc openssl-devel bzip2-devel libffi-devel -y
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
sudo tar xzf Python-3.9.7.tgz
cd Python-3.9.7
sudo ./configure --enable-optimizations
sudo make altinstall
python3.9 --version
sudo rm /usr/bin/python3
sudo ln -s /usr/local/bin/python3.9 /usr/bin/python3
python3 --version
sudo /usr/local/bin/python3.9 -m ensurepip --upgrade
sudo /usr/local/bin/python3.9 -m pip install --upgrade pip

# libraries
sudo yum install graphviz -y
sudo yum install python-pip -y
pip3 install graphviz
pip3 install pyyaml
