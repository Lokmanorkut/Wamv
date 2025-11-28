#!/usr/bin/env python3
"""
WAM-V Localization Launch File - DÜZELTME
robot_localization ile IMU + GPS füzyonu
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    pkg_share = get_package_share_directory('wamv_gz')
    
    ekf_config_path = os.path.join(pkg_share, 'config', 'ekf.yaml')
    navsat_config_path = os.path.join(pkg_share, 'config', 'navsat_transform.yaml')
    rviz_config_path = os.path.join(pkg_share, 'config', 'wamv_localization.rviz')
    
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='RViz2 başlatılsın mı?'
    )
    
    # WAM-V simülasyonu
    wamv_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('wamv_gz'),
                'launch',
                'wamv_launch.py'
            ])
        ])
    )
    
    # Map -> Odom static transform
    static_tf_map_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_map_odom',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        output='screen'
    )
    
    # NavSat Transform - GPS'i Odometry'ye çevirir
    navsat_transform = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        output='screen',
        parameters=[navsat_config_path],
        remappings=[
            ('imu/data', '/wamv/sensors/imu/imu/data'),
            ('gps/fix', '/wamv/sensors/gps/gps/fix'),
            ('odometry/filtered', '/odometry/global'),
            ('odometry/gps', '/wamv/gps/odom'),
            ('gps/filtered', '/wamv/gps/filtered')
        ]
    )
    
    # EKF Node - IMU + GPS füzyonu
    ekf_global = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_global_node',
        output='screen',
        parameters=[ekf_config_path],
        remappings=[
            ('odometry/filtered', '/odometry/global')
        ]
    )
    
    # RViz2 - Simülasyon başladıktan 3 saniye sonra başlat
    rviz = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=['-d', rviz_config_path] if os.path.exists(rviz_config_path) else [],
                condition=IfCondition(LaunchConfiguration('use_rviz'))
            )
        ]
    )
    
    return LaunchDescription([
        use_rviz_arg,
        wamv_simulation,
        static_tf_map_odom,
        # Simülasyon başladıktan sonra localization başlat
        TimerAction(
            period=2.0,
            actions=[navsat_transform, ekf_global]
        ),
        rviz,
    ])
