# -----------------------------------------------------------------------------
# Copyright 2023 Bernd Pfrommer <bernd.pfrommer@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

import launch
from launch.actions import DeclareLaunchArgument as LaunchArg
from launch.actions import OpaqueFunction
from launch.substitutions import LaunchConfiguration as LaunchConfig
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode


def launch_setup(context, *args, **kwargs):
    """Create composed driver + recorder node."""
    container = ComposableNodeContainer(
        name='libcaer_driver_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        # prefix=['xterm -e gdb -ex run --args'],
        composable_node_descriptions=[
            ComposableNode(
                package='libcaer_driver',
                plugin='libcaer_driver::Driver',
                name=LaunchConfig('camera_name'),
                parameters=[
                    {
                        'device_type': LaunchConfig('device_type'),
                        'device_id': 1,
                        'bias_sensitivity': 4,  # for dvxplorer
                        'statistics_print_interval': 2.0,
                        'camerainfo_url': '',
                        'frame_id': '',
                        'event_message_time_threshold': 1.0e-3,
                    },
                ],
            ),
            ComposableNode(
                package='rosbag2_composable_recorder',
                plugin='rosbag2_composable_recorder::ComposableRecorder',
                name='recorder',
                parameters=[
                    {
                        'topics': ['/event_camera/events'],
                        'bag_name': LaunchConfig('bag'),
                        'bag_prefix': LaunchConfig('bag_prefix'),
                    }
                ],
                extra_arguments=[{'use_intra_process_comms': True}],
            ),
        ],
        output='screen',
    )
    return [container]


def generate_launch_description():
    """Create simple node by calling opaque function."""
    return launch.LaunchDescription(
        [
            LaunchArg('camera_name', default_value=['event_camera'], description='camera name'),
            LaunchArg(
                'device_type',
                default_value=['dvxplorer'],
                description='device type (davis, dvxplorer...)',
            ),
            LaunchArg('bag', default_value=[''], description='name of output bag'),
            LaunchArg('bag_prefix', default_value=['events_'], description='prefix of output bag'),
            OpaqueFunction(function=launch_setup),
        ]
    )
