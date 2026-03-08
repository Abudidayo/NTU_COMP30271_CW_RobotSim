import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_ntu_robotsim = get_package_share_directory('ntu_robotsim')
    
    # Include the unified launch description with explore enabled
    launch_unified_explore = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ntu_robotsim, 'launch', 'unified.launch.py')
        ),
        launch_arguments={'explore': 'true'}.items()
    )

    return LaunchDescription([
        launch_unified_explore
    ])
