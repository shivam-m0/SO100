export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:~/so100/install

export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$(pwd)/install/so100_description/share
ros2 launch so100_simulation sim.launch.py