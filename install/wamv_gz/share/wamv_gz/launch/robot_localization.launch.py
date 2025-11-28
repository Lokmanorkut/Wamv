from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Config dosyası yolunu al
    pkg_share = get_package_share_directory('wamv_gz')
    config_file = os.path.join(pkg_share, 'config', 'robot_localization_config.yaml')
    
    # Launch argümanları
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    
    return LaunchDescription([
        # Sim time argümanı
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        
        # Navsat Transform Node - GPS'i UTM'ye çevirir
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform_node',
            output='screen',
            parameters=[
                config_file,
                {'use_sim_time': use_sim_time}
            ],
            remappings=[
                ('imu/data', '/wamv/sensors/imu/imu/data'),
                ('gps/fix', '/wamv/sensors/gps/gps/fix'),
                ('odometry/filtered', '/odometry/local'),
                ('odometry/gps', '/odometry/gps')
            ]
        ),
        
        # EKF Local Node - Odom frame'de lokalizasyon
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_local_node',
            output='screen',
            parameters=[
                config_file,
                {'use_sim_time': use_sim_time}
            ],
            remappings=[
                ('odometry/filtered', '/odometry/local')
            ]
        ),
        
        # EKF Global Node - Map frame'de GPS+IMU füzyonu
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_global_node',
            output='screen',
            parameters=[
                config_file,
                {'use_sim_time': use_sim_time}
            ],
            remappings=[
                ('odometry/filtered', '/odometry/global')
            ]
        ),
        
        # Static transform: wamv/base_link -> base_link (Nav2 için)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'wamv/base_link']
        ),
    ])
