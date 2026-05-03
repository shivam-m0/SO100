from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable

import os 


def generate_launch_description():
    pkg_name ='so100_description'
    sim_pkg = 'so100_simulation'

    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'so100.urdf')
    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()

    resource_path = os.path.join(get_package_share_directory(pkg_name), '..')

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        # We append the current path to ensure we don't overwrite existing system paths
        value=[resource_path]
    )




    #launch rviz

    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': False}]
    )

    gazebo = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
            launch_arguments={'gz_args': '-r empty.sdf'}.items(), 
    )
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Change the Gazebo message type from Model to JointState
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.JointState',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    node_joint_state_gui = Node(
    package='joint_state_publisher_gui',
    executable='joint_state_publisher_gui',
    # Do NOT set use_sim_time to True here if you want it to be the master
    parameters=[{'robot_description': robot_description , 'use_sim_time': False}]
)

    node_robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{'robot_description': robot_description,'use_sim_time': False}]
    )

    spawn_entity = Node(package='ros_gz_sim', executable='create',
                arguments=['-name', 'so100_arm', '-topic', 'robot_description'],
                output='screen')




    return LaunchDescription([
        node_robot_state_publisher,
        node_rviz,
        gazebo,
        spawn_entity,
        bridge,
        set_gz_resource_path,
        node_joint_state_gui
    ])