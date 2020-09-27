#!/bin/bash

set -ex

echo "Fetching auto stop script from https://raw.githubusercontent.com/manojlds/sagemaker-lifecycle/master/auto_stop_idle.py"

wget -O auto_stop_idle.py https://raw.githubusercontent.com/manojlds/sagemaker-lifecycle/master/auto_stop_idle.py

echo "Setting up cron with the auto stop script"


if ! (crontab -l 2>/dev/null | grep "auto_stop_idle.py"); then
    (crontab -l 2>/dev/null; echo -e "SAGEMAKER_JUPYER_IDLE_TIME=60\nSAGEMAKER_JUPYTER_PORT=8443\nSAGEMAKER_JUPYTER_SSL=true\n*/5 * * * * '$PWD/auto_stop_idle.py | tee -a /home/ec2-user/SageMaker/auto_stop_idle.log'") | crontab -
fi

