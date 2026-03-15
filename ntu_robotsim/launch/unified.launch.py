import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetRemap
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition


def generate_launch_description():
    pkg_ntu_robotsim = get_package_share_directory('ntu_robotsim')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_odom_tf = get_package_share_directory('odom_to_tf_ros2')
    pkg_octomap_server = get_package_share_directory('octomap_server2')

    nav2_params_path = os.path.join(pkg_ntu_robotsim, 'config', 'nav2_params.yaml')
    explore_params_path = os.path.join(pkg_ntu_robotsim, 'config', 'explore_params.yaml')

    # Launch arguments
    declare_explore_cmd = DeclareLaunchArgument(
        'explore',
        default_value='false',
        description='Whether to start autonomous exploration'
    )

    # Use cwmaze as it is more complete and matches robot config
    launch_maze = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_ntu_robotsim, 'launch', 'cwmaze.launch.py'))
    )
    
    launch_robot = IncludeLaunchDescription(
        # This will use single_robot_maze_sim.yaml which spawns in cwmaze
        PythonLaunchDescriptionSource(os.path.join(pkg_ntu_robotsim, 'launch', 'single_robot_sim.launch.py')),
        launch_arguments={'world': 'maze'}.items() 
    )

    launch_odom_tf = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_odom_tf, 'launch', 'atlas_odom_to_tf.launch.py'))
    )

    launch_octomap = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_octomap_server, 'launch', 'octomap_filtered.launch.py'))
    )

    run_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_ntu_robotsim, 'config', 'single_robot.rviz')]
    )

    # Launch Nav2 with cmd_vel remapping
    launch_nav2 = TimerAction(
        period=5.0,
        actions=[
            GroupAction(
                actions=[
                    SetRemap(src='/cmd_vel', dst='/atlas/cmd_vel'),
                    IncludeLaunchDescription(
                        PythonLaunchDescriptionSource(os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')),
                        launch_arguments={
                            'params_file': nav2_params_path,
                            'use_sim_time': 'true',
                            'use_rviz': 'false'
                        }.items()
                    )
                ]
            )
        ]
    )

    # Explore Lite Node for autonomous navigation
    node_explore_lite = Node(
        package='explore_lite',
        executable='explore',
        name='explore_node',
        output='screen',
        parameters=[explore_params_path, {'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('explore'))
    )

    launch_explore_with_delay = TimerAction(
        period=15.0,
        actions=[node_explore_lite]
    )

    static_map_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'atlas/odom']
    )

    return LaunchDescription([
        declare_explore_cmd,
        launch_maze,
        launch_robot,
        launch_odom_tf,
        launch_octomap,
        run_rviz,
        launch_nav2,
        launch_explore_with_delay,
        static_map_tf
    ])
