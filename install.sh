#!/bin/sh

# setup piconzero and all dependancies for the bottle filler


sudo apt-get install python-smbus python3-smbus python-dev python3-dev python
sudo cat >>/boot/config.txt <<EOF
dtparam=i2c1=on
dtparam=i2c_arm=on
EOF

# i2cdetect -y 1

#wget http://4tronix.co.uk/piconz.sh -O piconz.sh
#bash piconz.sh

git clone https://github.com/4tronix/PiconZero.git

pip install enum
pip install smbus

