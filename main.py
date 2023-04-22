from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os
import torch
import sys
import math
sys.path.append("/PIR_SGAN-main/sgan")
sys.path.append("/PIR_SGAN-main/rrt_mpc")
from attrdict import AttrDict

import numpy as np
from sgan.sgan.data.loader import data_loader
from sgan.sgan.models import TrajectoryGenerator
from sgan.sgan.losses import displacement_error, final_displacement_error
from sgan.sgan.utils import relative_to_abs, get_dset_path
from rrt_mpc.robot import robot

r1 = robot([0, 0], 1)

def get_generator(checkpoint):
    args = AttrDict(checkpoint['args'])
    generator = TrajectoryGenerator(
        obs_len=args.obs_len,
        pred_len=args.pred_len,
        embedding_dim=args.embedding_dim,
        encoder_h_dim=args.encoder_h_dim_g,
        decoder_h_dim=args.decoder_h_dim_g,
        mlp_dim=args.mlp_dim,
        num_layers=args.num_layers,
        noise_dim=args.noise_dim,
        noise_type=args.noise_type,
        noise_mix_type=args.noise_mix_type,
        pooling_type=args.pooling_type,
        pool_every_timestep=args.pool_every_timestep,
        dropout=args.dropout,
        bottleneck_dim=args.bottleneck_dim,
        neighborhood_size=args.neighborhood_size,
        grid_size=args.grid_size,
        batch_norm=args.batch_norm)
    generator.load_state_dict(checkpoint['g_state'])
    generator.train()
    return generator

def evaluate2(args, loader, generator, num_samples):
    with torch.no_grad():
        for batch in loader:
            batch = [tensor for tensor in batch]
            (obs_traj, obs_traj_rel, seq_start_end) = batch

            for _ in range(num_samples):
                pred_traj_fake_rel = generator(
                    obs_traj, obs_traj_rel, seq_start_end
                )
                pred_traj_fake = relative_to_abs(
                    pred_traj_fake_rel, obs_traj[-1]
                )

        return pred_traj_fake


dir_name = "/PIR_SGAN-main/sgan/models/sgan-models"
filenames = os.listdir(dir_name)
filenames.sort()
paths = [
    os.path.join(dir_name, file_) for file_ in filenames
]
for path in paths:
    checkpoint = torch.load(path, map_location=torch.device("cpu"))
    generator = get_generator(checkpoint)
    _args = AttrDict(checkpoint['args'])

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def check_dist(trajs, robot_trajs, numofplayers, radius):
    new_trajs = robot_trajs
    plist = []

    # Loop runs for the number of players
    for i in range(numofplayers, 0, -1):

        # Eculidean Distance
        dist = np.sqrt(
                np.square(trajs[-(i)][-2] - robot_trajs[-1][-2] ) +         # x coordinate
                np.square(trajs[-(i)][-1] - robot_trajs[-1][-1] )          # y coordinate
                )
        #print(dist)

        # If distance is within a certain radius, all the last 8 positions of person is appended in a new list called new_trajs
        # Note: new_trajs containts 8 positions of player i THEN player i+1 (if the criteria is met that is)
        if dist < radius:
            person = trajs[-i][1]
            plist.append(person)
            l = 0
            while l < len(trajs):
                if trajs[l][1] == person:
                    new_trajs.append(trajs[l])
                l += 1

    #print("new_trajs", new_trajs)
    #print("Same" if len(new_trajs) == len(trajs) else "Not Same")

    return new_trajs, plist

@app.post("/get_preds")
async def get_preds(data: dict):
    ptrajs = data['ptrajs']
    ptrajs = [[float(val) for val in row] for row in ptrajs]
    rtrajs = data['rtrajs']
    rtrajs = [[float(val) for val in row] for row in rtrajs]

    radius = int(data["radius"])
    numofplayers = int(data['numberOfPeople'])
    new_trajs, plist = check_dist(ptrajs, rtrajs, numofplayers, radius)

    assert(len(new_trajs) % 8 == 0)

    preds = None

    # check if there are no collisions happening
    if (len(new_trajs) == 8):
        return {"res": 0, "plist": plist, "preds": preds}

    assert(len(plist) != 0)

    _, loader = data_loader(_args, path, np.asarray(new_trajs))
    preds = evaluate2(_args, loader, generator, 1)

    return {"res": 1, "plist": plist, "preds": preds.tolist()}

@app.post("/set_goal")
async def set_goal(data: dict):
    # data contains:
    # goalX: float
    # goalY: float
    goalX = float(data.get("goalX"))
    goalY = float(data.get("goalY"))
    r1.update_goal([goalX, goalY])
    return {"res": 0}


@app.post("/get_robot")
async def get_robot(data: dict):
    # data contains:
    # ptrajs: Array of previous 8 positions of all the humans
    # ppath: Array of 8 next positions of all people. 
    # rpath: Array of the previous 8 positions of the robot
    num_of_steps =8
    ptrajs = data['ppath']
    num_persons = len(ptrajs/num_of_steps)
    # obs_sta]=[]
    obstacles_list=[]
    person_iter=0
    for iter in range(num_persons):
        x_start = ptrajs[iter][2]
        y_start = ptrajs[iter][2]

        x_end = ptrajs[iter+(num_of_steps-1)*num_persons-1][2]
        y_end = ptrajs[iter+(num_of_steps-1)*num_persons-1][3]

        center_x = (x_start+x_end)/2
        center_y = (y_start+y_end)/2
        dx=x_start-center_x
        dy=y_start-center_y
        obs_radius=math.hypot(dx, dy)
        obstacles_list.append([center_x, center_y, obs_radius])

    r1.obstacle_list = obstacles_list
    
    # r1.path = data['ppath']
    # r1.rpath = data['rpath']
    r1.find_path_to_goal(True)
    rpath =r1.get_next_steps(8)
    # rpath = []
    # for i in range(8):
    #     rpath.append(r1.path_x[i], r1.path_y[i])
    return {"rpath": rpath}
