from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable
from launch.actions import ExecuteProcess
from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit

import os


def generate_launch_description():

    pkg_name = 'so100_description'

    urdf_file = os.path.join(get_package_share_directory(pkg_name), 'urdf', 'so100.urdf')

    with open(urdf_file, 'r') as infp:
        robot_description = infp.read()


    resource_path = os.path.join(get_package_share_directory(pkg_name), '..')

    set_gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[resource_path]
    )
    
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(get_package_share_directory(pkg_name), 'rviz', 'so100.rviz')],
    )

    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description ,'use_sim_time' : True}]
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
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.JointState',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
        ],
        parameters=[{
         "qos_overrides./tf_static.publisher.durability": "transient_local"
     }],
        output='screen'
    )

    node_joint_state_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
    )


    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'so100_arm', '-topic', 'robot_description'],
        output='screen'
    )
    load_joint_state_broadcaster = ExecuteProcess(
    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'joint_state_broadcaster'],
    output='screen'
)

    load_arm_controller = ExecuteProcess(
    cmd=['ros2', 'control', 'load_controller', '--set-state', 'active', 'arm_controller'],
    output='screen'
)
    
    load_controllers_after_spawn = RegisterEventHandler(
    event_handler=OnProcessExit(
        target_action=spawn_entity,
        on_exit=[load_joint_state_broadcaster, load_arm_controller],
    )
)

    return LaunchDescription([
        node_joint_state_gui,
        set_gz_resource_path,       
        node_robot_state_publisher,
        bridge,    
        gazebo,                     
        spawn_entity,              
        node_rviz,
        load_controllers_after_spawn
    ])