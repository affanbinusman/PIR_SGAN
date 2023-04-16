from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os
import torch
import sys
sys.path.append("/PIR_SGAN-main/sgan/")
from attrdict import AttrDict

import numpy as np
from sgan.data.loader import data_loader
from sgan.models import TrajectoryGenerator
from sgan.losses import displacement_error, final_displacement_error
from sgan.utils import relative_to_abs, get_dset_path

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
    new_trajs = list()

    # Loop runs for the number of players
    for i in range(1, numofplayers + 1):

        # Eculidean Distance
        dist = np.sqrt(
                np.square(trajs[-(i)][-2] - robot_trajs[-1][-2] ) +         # x coordinate
                np.square(trajs[-(i)][-1] - robot_trajs[-1][-1] )          # y coordinate
                )
        #print(dist)

        # If distance is within a certain radius, all the last 8 positions of person is appended in a new list called new_trajs
        # Note: new_trajs containts 8 positions of player i THEN player i+1 (if the criteria is met that is)
        if dist < radius:
            person = trajs[-1][1]
            l = 0
            while l < len(trajs):
                if trajs[l][1] == person:
                    new_trajs.append(trajs[l])
                l += 1

    #print("new_trajs", new_trajs)
    #print("Same" if len(new_trajs) == len(trajs) else "Not Same")

    return new_trajs

@app.post("/get_preds")
async def response(data: dict):
    trajs = list(data.values())[0]
    trajs = [[float(val) for val in row] for row in trajs]
    
    robot_trajs = [[0, 0, 50, 50], [10, 0, 200, 200]]
    radius = 50
    numofplayers = 2        # Need this from front end
    new_trajs = check_dist(trajs, robot_trajs, numofplayers, radius)        # How to integrate this new list. I tried replacing it and it wouldn't work if the list does not have info of all people
    
    _, loader = data_loader(_args, path, np.asarray(trajs))
    preds = evaluate2(_args, loader, generator, 1)
    return {"preds": preds.tolist()}
