from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable

import os


def generate_launch_description():
    pkg_name = 'so100_description'

    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'so100.urdf')
    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()

    resource_path = os.path.join(get_package_share_directory(pkg_name), '..')

    # Must come FIRST so Gazebo finds meshes
    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[resource_path]
    )

    rviz_config = os.path.join(get_package_share_directory(pkg_name), 'rviz', 'so100.rviz')

    # use_sim_time: True so RViz follows Gazebo's /clock
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # /joint_states: GZ->ROS only ('[') so Gazebo publishes state to ROS
    # /clock: GZ->ROS only ('[') so nodes with use_sim_time=True get Gazebo clock
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.JointState',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        output='screen'
    )

    # GUI stays on wall time — it is the master driving joint positions.
    # If set to sim time it can freeze waiting for /clock and sliders stop working.
    node_joint_state_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        parameters=[{'robot_description': robot_description, 'use_sim_time': False}]
    )

    # use_sim_time: True so TF transforms are stamped with Gazebo clock,
    # keeping RViz in sync with the simulation
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'so100_arm', '-topic', 'robot_description'],
        output='screen'
    )

    return LaunchDescription([
        node_joint_state_gui,
        set_gz_resource_path,       # 1. env var before anything starts
        node_robot_state_publisher,
         bridge,     # 2. TF publisher
        gazebo,                     # 4. simulation
        spawn_entity,               # 5. spawn robot into Gazebo                 # 6. ROS <-> Gazebo bridge
                node_rviz,                  # 3. visualiser

            # 7. joint controller GUI
    ])