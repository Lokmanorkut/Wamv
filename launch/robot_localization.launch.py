from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('wamv_gz')
    config_file = os.path.join(pkg_share, 'config', 'ekf_localization.yaml')
    
    return LaunchDescription([
        # Static TF: base_link'ten IMU'ya
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_imu',
            arguments=['0', '0', '0', '0', '0', '0', 
                      'wamv/base_link', 'wamv/wamv/imu_wamv_link/imu_wamv_sensor']
        ),
        
        # Static TF: base_link'ten GPS'e
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_gps',
            arguments=['0', '0', '0', '0', '0', '0', 
                      'wamv/base_link', 'wamv/wamv/gps_wamv_link/navsat']
        ),
        
        # Navsat Transform Node
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform_node',
            output='screen',
            parameters=[config_file],
            remappings=[
                ('imu', '/wamv/sensors/imu/imu/data'),
                ('gps/fix', '/wamv/sensors/gps/gps/fix'),
                ('odometry/filtered', '/odometry/filtered'),
                ('gps/filtered', '/gps/filtered'),
                ('odometry/gps', '/odometry/gps')
            ]
        ),
        
        # EKF Node
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[config_file],
            remappings=[
                ('odometry/filtered', '/odometry/filtered'),
                ('/set_pose', '/initialpose')
            ]
        )
    ])
