from dataclasses import dataclass

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus

class CreateGoal(Node):
    def __init__(self):
        super().__init__(node_name="create_goal")

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        @dataclass
        class Goal:
            x_pos: float
            y_pos: float
            z_pos: float

            x_ori: float
            y_ori: float
            z_ori: float
            w_ori: float

        self.goal = Goal(12.5192, 14.4956, 0.0, 0.0, 0.0, 0.0, 1.0)

    def send_goal(self):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.pose.position.x = self.goal.x_pos
        goal_msg.pose.pose.position.y = self.goal.y_pos
        goal_msg.pose.pose.orientation.w = self.goal.w_ori
    
        self._action_client.wait_for_server()
        
        send_goal_future = self._action_client.send_goal_async(goal_msg)
        #First callback: Was the goal accepted by the server?
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected :(')
            return

        self.get_logger().info('Goal accepted!')
        #Second callback: What was the final result?
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        status = future.result().status
        
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Success, Goal reached.')
        else:
            #auto restart if the goal failed, since it commonly fails for zero reason
            self.get_logger().warn(f'Goal failed with status: {status}. Restarting...')
            self.restart_navigation()

    def restart_navigation(self):
        if self.goal:
            # Re-send the goal since it failed
            self.send_goal()


def main(args=None):
    rclpy.init(args=args)
    create_goal = CreateGoal()
    rclpy.spin(create_goal)
    create_goal.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()