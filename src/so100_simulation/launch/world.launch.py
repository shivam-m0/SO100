from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription

import os 


def generate_launch_description():
    pkg_name ='so100_description'
    sim_pkg = 'so100_simulation'

    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'so100.urdf')
    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()

    node_robot_state_publisher = Node(
    package='robot_state_publisher',
    executable='robot_state_publisher',
    output='screen',
    parameters=[{'robot_description': robot_description}]
    )


    node_joint_state_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    #launch rviz

    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
    )




    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_gui,
        node_rviz,
    ])