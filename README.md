AWS Sagemaker Lifecycle scripts

`auto_stop_idle.py` - Uses Jupyter API to check if notebooks/kernels are idle and shuts down the notebook instance if it has been idle beyond a give idle timeout.

`on-start.sh.tmpl` is Terraform compatible template file that can be used to configure appropriate start / create lifecycle script for use with Terraform.