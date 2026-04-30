from dataclasses import dataclass

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped 

class CreateGoal(Node):
    def __init__(self):
        super().__init__(node_name="create_goal")

        @dataclass
        class Goal:
            x_pos: float
            y_pos: float
            z_pos: float

            x_ori: float
            y_ori: float
            z_ori: float
            w_ori: float

        self.goal = Goal(12.5192, 14.4956, 0.0, 0.0, 0.0, 0.0, 0.0)

        self.goal_publisher = self.create_publisher(
            msg_type=PoseStamped,
            topic="/goal_pose",
            qos_profile=1,
        )

        self.create_timer(2, self.Publish_Goal)

    def Publish_Goal(self):
        self.curr_ts = self.get_clock().now()

        msg = PoseStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.curr_ts.to_msg()

        msg.pose.position.x = self.goal.x_pos
        msg.pose.position.y = self.goal.y_pos
        msg.pose.position.z = self.goal.z_pos

        msg.pose.orientation.x = self.goal.x_ori
        msg.pose.orientation.y = self.goal.y_ori
        msg.pose.orientation.z = self.goal.z_ori
        msg.pose.orientation.w = self.goal.w_ori

        self.goal_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    create_goal = CreateGoal()
    rclpy.spin(create_goal)
    create_goal.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()