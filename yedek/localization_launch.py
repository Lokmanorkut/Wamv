from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_share = get_package_share_directory('wamv_gz')

    ekf_config = os.path.join(pkg_share, 'config', 'ekf.yaml')
    navsat_config = os.path.join(pkg_share, 'config', 'navsat_transform.yaml')

    return LaunchDescription([

        # 1) EKF: IMU + GPS fused → odom -> base_link + map -> odom TF üretir
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_config],
            remappings=[
                ('imu0', '/wamv/sensors/imu/imu/data'),
                ('gps0', '/gps/filtered'),
            ]
        ),

        # 2) NavSat transform — IMU + GPS -> GPS Odom produces /gps/filtered
        Node(
            package='robot_localization',
            executable='navsat_transform_node',
            name='navsat_transform_node',
            output='screen',
            parameters=[navsat_config],
            remappings=[
                ('imu/data', '/wamv/sensors/imu/imu/data'),
                ('gps/fix', '/wamv/sensors/gps/gps/fix'),
                ('odometry/filtered', '/odometry/filtered'),
                ('gps/filtered', '/gps/filtered'),
            ]
        )
    ])

