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
                #print(f"obs_traj of size {len(obs_traj)}:")
                #print(obs_traj)
                #print("pred_traj_fake:")
                #print(pred_traj_fake)

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

@app.post("/get_preds")
async def response(data: dict):
    trajs = list(data.values())[0]
    trajs = [[float(val) for val in row] for row in trajs]
    _, loader = data_loader(_args, path, np.asarray(trajs))
    preds = evaluate2(_args, loader, generator, 1)
    return {"preds": preds.tolist()}
