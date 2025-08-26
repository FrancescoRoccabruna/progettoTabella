#!/bin/bash


shopt -s expand_aliases
alias obedge='/opt/airpim/bin/obedge'

# --------------------------------------------------------------------------------------------#

echo
echo "[ARCONVERT]"
echo

# --------------------------------------------------------------------------------------------#

<< ////

# Sample(s):

## 1. scan and react by blinking led
      obedge run -s ft232 -e "i:led/blink=5000 100 1"

////

# --------------------------------------------------------------------------------------------#


echo 
obedge info
echo

# --------------------------------------------------------------------------------------------#

# setta emergenza
#echo "1" > /sys/class/ionopi/relay/o3

while : ;
do
    obedge run  -i "init.py sqlite:testa.sqlite" -q mqtt,auth,10.0.0.179:51883,feed,admin -s FTDI_FT232R --queue-username test --queue-password test  --name TEST -e "p:./arconvert.py"  --console
    wait -n
    sleep 3
done

