#!/usr/bin/env bash

# Set for debug
#set -x

pip3 install virtualenv
virtualenv ./

source bin/activate

pip3 install pyTelegramBotAPI google-api-python-client Flask

echo "============================================================"
echo "Installation finished now do 'source bin/activate' to activate"
echo "the virtualenv environment"
echo "============================================================"

