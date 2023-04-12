
import numpy as np
from rrt_plan import *
import math
import matplotlib.pyplot as plt
from nmpc import *


ROBOT_RADIUS = 1.5
VMAX = 2
VMIN = 0.1

# collision cost parameters
Qc = 5.
kappa = 4.

# nmpc parameters
HORIZON_LENGTH = int(4)
NMPC_TIMESTEP = 0.3
upper_bound = [(1/np.sqrt(2)) * VMAX] * HORIZON_LENGTH * 2
lower_bound = [-(1/np.sqrt(2)) * VMAX] * HORIZON_LENGTH * 2

class robot:
    def __init__(self, start_pos, ID) -> None:

        self.ID=ID
        self.local_planner_ID=0
        self.cur_pos=start_pos
        self.goal=[0,0]
        self.sensory_radius=10
        self.start_position=start_pos
        self.state=[self.cur_pos[0], self.cur_pos[1], 0, 0]
        self.reached_goal=False
        self.obstacle_list=[]

    def update_goal(self, goal):
        self.goal=goal


    def find_path_to_goal(self, show_animation):
        self.obstacle_list=[[2,3,1]]  
        fov_r=0.5
        x_path=[]
        y_path=[]

        min_val=-5
        max_val=20
        # Set Initial parameters
        # print(min_val)
        # print(max_val)
        rrt_star = RRTStar(
            start=self.start_position,
            goal=self.goal,
            rand_area=[min_val, max_val],
            obstacle_list=self.obstacle_list,
            expand_dis=1,
            robot_radius=0.8)
        path = rrt_star.planning(animation=True)

        if path is None:
            print("Cannot find path")
        else:
            print("found path!!")
            

            # Draw final path
            
            if show_animation:
                # print("drawing graph")
                rrt_star.draw_graph()
                iter=0
                for (x,y) in path:
                    if iter: 
                        x_path.append(x)
                        y_path.append(y)
                    iter=1
                plt.plot(x_path, y_path, 'r--')
                plt.grid(True)

        x_path.reverse()
        y_path.reverse()

        goal = [x_path[-1], y_path[-1]]
        cyaw=[]
        cx=[]
        cy=[]
        cx1, cy1, cyaw1, ck, s = calc_spline_course(
                x_path, y_path, ds=0.1)
        cx= [round(num, 1) for num in cx1]
        cy= [round(num, 1) for num in cy1]
        cyaw= [round(num, 1) for num in cyaw1]
        self.path_x=cx
        self.path_y=cy
        self.path_yaw=cyaw
        self.path_k=ck

        # plt.clf()
    # for stopping simulation with the esc key.
        plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])

        plt.plot(cx,cy,'-y')
        plt.pause(0.1)

    plt.show()



    print("FOUND Path!!")
    
    def drive_along_path(self):
        target_speed = 10.0 / 3.6  # simulation parameter km/h -> m/s

        # sp = calc_speed_profile(self.path_yaw, target_speed)
        while(not self.reached_goal):
            self.do_simulation()

    def do_simulation(self):

        start = np.array([self.state[0], self.state[1]])
        p_desired = np.array([self.goal[0], self.goal[1]])
        NUMBER_OF_TIMESTEPS=1
        goal_thresh=0.5
        robot_state = start
        robot_state_history = np.empty((4, NUMBER_OF_TIMESTEPS))
        plt.plot(self.goal[1],self.goal[0],'xk')

        for i in range(NUMBER_OF_TIMESTEPS):
            # predict the obstacles' position in future
            obstacle_predictions=np.zeros((len(self.obstacle_list),4))
            ind=0
            for obs in self.obstacle_list:
                
                pos=[]
                print("hellooo",obs, ind)
                obstacle_predictions[ind][0] = obs[0]
                obstacle_predictions[ind][1] = obs[1]
                obstacle_predictions[ind][2] = 0
                obstacle_predictions[ind][3] = 0        

                ind+=1
            # ob_iter=0
            # if ind==0:
            #     ind=1
            # for ob in self.obstacle_list:
            #     obstacle_predictions[ind-1][0]=ob[0]
            #     obstacle_predictions[ind-1][1]=ob[1]
            #     obstacle_predictions[ind-1][2]=0
            #     obstacle_predictions[ind-1][3]=0
            #     ind+=1
            obstacle_predictions = predict_obstacle_positions(obstacle_predictions)    
            xref = compute_xref(robot_state, p_desired,
                                HORIZON_LENGTH, NMPC_TIMESTEP)
            print(obstacle_predictions)
            print(xref)
            # compute velocity using nmpc
            vel, velocity_profile = compute_velocity(
                robot_state, obstacle_predictions, xref)
            robot_state = update_state(robot_state, vel, TIMESTEP)
            print("Robot State :", robot_state)
            robot_state_history[:2, i] = robot_state
            self.state=[robot_state[0],robot_state[1], vel[0], vel[1]]
            self.cur_pos=self.state[:2]
        if np.linalg.norm(np.array([self.cur_pos[0], self.cur_pos[1]])- p_desired)<0.2:
            self.reached_goal=True
            print("REACHED GOAL")
        plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])

        plt.plot(robot_state[0], robot_state[1], 'or')
        plt.pause(0.1)


    def get_sensor_readings_and_update(self):
        pass

def calc_speed_profile(cyaw, target_speed):
    speed_profile = [target_speed] * len(cyaw)

    direction = 1.0

    # Set stop point
    for i in range(len(cyaw) - 1):
        dyaw = abs(cyaw[i + 1] - cyaw[i])
        switch = math.pi / 4.0 <= dyaw < math.pi / 2.0

        if switch:
            direction *= -1

        if direction != 1.0:
            speed_profile[i] = - target_speed
        else:
            speed_profile[i] = target_speed

        if switch:
            speed_profile[i] = 0.0

    # speed down
    for i in range(len(cyaw) - 1):
        speed_profile[-i] = target_speed / (100 - i)
        if speed_profile[-i] <= 1.0 / 3.6:
            speed_profile[-i] = 1.0 / 3.6

    return speed_profile



r1=robot([0,0],1)
r1.update_goal([15,10])
r1.find_path_to_goal(True)
r1.drive_along_path()