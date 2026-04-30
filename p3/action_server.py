from dataclasses import dataclass
from time import sleep

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus

class CreateGoal(Node):
    def __init__(self):
        super().__init__(node_name="create_goal")

        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

        #Goal holding dataclass
        @dataclass
        class Goal:
            x_pos: float
            y_pos: float
            z_pos: float

            x_ori: float
            y_ori: float
            z_ori: float
            w_ori: float

        #Hardcoded final goal
        self.goal = Goal(12.5192, 14.4956, 0.0, 0.0, 0.0, 0.0, 1.0)

        #Long startup sleep, this was due to when the local_cost map failed to load fast enough
        #it would just instantly think it was at the destination, so this silly long delay helped with that
        sleep(30)

        #Send the first goal
        self.send_goal()

    def send_goal(self):
        curr_ts = self.get_clock().now()
        goal_msg = NavigateToPose.Goal()

        ##Create the message
        goal_msg.pose.header.frame_id='map'
        goal_msg.pose.header.stamp = curr_ts.to_msg()

        goal_msg.pose.pose.position.x = self.goal.x_pos
        goal_msg.pose.pose.position.y = self.goal.y_pos
        goal_msg.pose.pose.orientation.w = self.goal.w_ori

        #Wait for the server to be partially up
        self._action_client.wait_for_server()
        

        send_goal_future = self._action_client.send_goal_async(goal_msg)
        #Get the response from the server and handle it with it a function
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        #The message from the server
        goal_handle = future.result()
        
        #IF the goal was not accepted, then try again
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected, Restarting...')
            self.restart_navigation()
            return
        
        self.get_logger().info('Goal accepted!')
        #Get the response from the server 
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        #Final result
        status = future.result().status
        
        ##If sucesses then just stop
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info('Success, Goal reached.')
        elif status == GoalStatus.STATUS_EXECUTING:
            ##If the goal is still in progress then just let it keep going
            self.get_logger.info('Executing, Goal in progress')
        else:
            #auto restart if the goal failed, since it commonly fails for zero reason
            self.get_logger().warn(f'Goal failed with status: {status}. Restarting...')
            self.restart_navigation()

    def restart_navigation(self):
        sleep(0.25) #Technically this should be an async sleep, but what ever
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