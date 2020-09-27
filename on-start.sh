#!/bin/bash

set -ex

echo "Fetching auto stop script from https://raw.githubusercontent.com/manojlds/sagemaker-lifecycle/master/auto_stop_idle.py"

wget -O auto_stop_idle.py https://raw.githubusercontent.com/manojlds/sagemaker-lifecycle/master/auto_stop_idle.py

echo "Setting up cron with the auto stop script"

export SAGEMAKER_JUPYER_IDLE_TIME=60
export SAGEMAKER_JUPYTER_PORT=8443
export SAGEMAKER_JUPYTER_SSL=true

(crontab -l 2>/dev/null; echo "*/5 * * * * '$DIR/auto_stop_idle.py | tee -a /home/ec2-user/SageMaker/auto_stop_idle.log'") | crontab -

