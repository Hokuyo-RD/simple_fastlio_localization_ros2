import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def launch_setup(context, *args, **kwargs):
    # YAMLファイルからパラメータを読み込むためのパス
    # get_package_share_directory を使ってパッケージの共有ディレクトリを取得し、
    # その中に YAML ファイルを配置するのが一般的です。
    package_share_directory = get_package_share_directory('simple_fastlio_localization')
    param_file_path = os.path.join(package_share_directory, 'config', 'localization_params.yaml')

    # launchファイルで定義された引数を取得 (YAMLからの値を上書きするため)
    map_file = LaunchConfiguration('map_file').perform(context)
    initial_pose = LaunchConfiguration('initial_pose').perform(context)
    frames_accumulate = LaunchConfiguration('frames_accumulate').perform(context)
    min_registration_distance = LaunchConfiguration('min_registration_distance').perform(context)
    async_registration = LaunchConfiguration('async_registration').perform(context)
    publish_2d_pose = LaunchConfiguration('publish_2d_pose').perform(context)
    visualize_registration_result = LaunchConfiguration('visualize_registration_result').perform(context)
    enable_sound = LaunchConfiguration('enable_sound').perform(context)
    enable_lio_only_update = LaunchConfiguration('enable_lio_only_update').perform(context)

    # トピックリマッピングの引数を取得
    odom_topic = LaunchConfiguration('odom_topic').perform(context)
    cloud_odom_topic = LaunchConfiguration('cloud_odom_topic').perform(context)
    pose_topic = LaunchConfiguration('pose_topic').perform(context)
    map_topic = LaunchConfiguration('map_topic').perform(context)

    # initial_pose の文字列をリストに変換
    # initial_pose_list = [float(x) for x in initial_pose_str.split()] if initial_pose_str else []

    return [
        Node(
            package='simple_fastlio_localization',
            executable='localization_node',
            name='localization_node',
            output='screen',
            parameters=[
                param_file_path,
                {
                  'map_file': map_file,
                  'initial_pose': initial_pose,
                  'frames_accumulate': int(frames_accumulate),
                  'min_registration_distance': float(min_registration_distance),
                  'asynchronous_registration': async_registration.lower() == 'true',
                  'publish_2d_pose': publish_2d_pose.lower() == 'true',
                  'visualize_registration_result': visualize_registration_result.lower() == 'true',
                  'enable_sound': enable_sound.lower() == 'true',
                  'enable_lio_only_update': enable_lio_only_update.lower() == 'true',
                }],
            remappings=[
                ('/Odometry', odom_topic),
                ('/cloud_registered', cloud_odom_topic),
                ('/estimated_pose', pose_topic),
                ('/map_cloud', map_topic),
            ]
        )
    ]

def generate_launch_description():
    package_path = get_package_share_directory('simple_fastlio_localization')
    default_rviz_config_path = os.path.join(package_path, 'rviz', 'loc.rviz')

    return LaunchDescription([
        DeclareLaunchArgument('map_file', default_value='/home/colcon_ws/src/hokuyo_navigation2/map/expo_ros2.pcd', description='Path to the map file'),
        # DeclareLaunchArgument('initial_pose', default_value='-1.002715729700867 0.21954120489681372 -0.23875123379999508 0.0162312792 0.0129877045 0.6142911386 0.7995398734', description='Initial pose as a string: "x y z roll pitch yaw w"'),
        DeclareLaunchArgument('initial_pose', default_value='0.0 0.0 0.0 0.0162312792 0.0129877045 0.7142911386 0.6995398734', description='Initial pose as a string: "x y z roll pitch yaw w"'),
        DeclareLaunchArgument('frames_accumulate', default_value='1', description='No. of frames accumulate for matching'),
        DeclareLaunchArgument('min_registration_distance', default_value='0.0', description='Minimum distance for registration'),
        DeclareLaunchArgument('async_registration', default_value='true', description='Async registration'),
        DeclareLaunchArgument('publish_2d_pose', default_value='false', description='Publish 2D pose as /map -> /odom transform'),
        DeclareLaunchArgument('visualize_registration_result', default_value='false', description='Visualize registration result with color coding'),
        DeclareLaunchArgument('enable_sound', default_value='true', description='Enable sound notification for registration results'),
        DeclareLaunchArgument('enable_lio_only_update', default_value='true', description='Update self-pose on receiving lio without pointcloud registration'),
        DeclareLaunchArgument('rviz', default_value='true', description='Launch Rviz'),
        DeclareLaunchArgument('rviz_config', default_value=default_rviz_config_path, description='Path to the RViz config file'),

        DeclareLaunchArgument('odom_topic', default_value='/hokuyo_lio/lidar_odom', description='Odometry topic name'),
        DeclareLaunchArgument('cloud_odom_topic', default_value='/hokuyo_lio/aligned_scan_points', description='Odometry frame cloud topic name'),
        DeclareLaunchArgument('pose_topic', default_value='/estimated_pose', description='Estimated pose output topic name'),
        DeclareLaunchArgument('map_topic', default_value='/map_cloud', description='Map cloud output topic name'),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz',
            arguments=['-d', LaunchConfiguration('rviz_config')],
            output='screen',
            condition=IfCondition(LaunchConfiguration('rviz'))
        ),

        TimerAction(
            period=3.0,
            actions=[
                OpaqueFunction(function=launch_setup)
            ]
        )
    ])