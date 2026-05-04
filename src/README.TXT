export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:~/so100/install

export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:$(pwd)/install/so100_description/share
ros2 launch so100_simulation sim.launch.py


# Tell ROS to use Gazebo Harmonic (v8)
export GZ_VERSION=8

# Tell Gazebo where the ROS plugin lives
export GZ_SIM_SYSTEM_PLUGIN_PATH=$GZ_SIM_SYSTEM_PLUGIN_PATH:/opt/ros/humble/lib