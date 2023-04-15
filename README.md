# PIR_SGAN

Project repository for simulating a socially compliant robot which avoids human path trajectories. 
Based on the SGAN model for finding human path trajectories in a Docker container, simulations are performed using p5.js on a chrome and FastAPI backend.

## Running the Docker container
1. Build the container 
```
docker build . --platform=linux/amd64 -t sgan
```
2. Run the container 
```
docker run --platform=linux/amd64 -p 8000:8000 -it sgan
```

## Running the FastAPI based server
```
cd scripts
uvicorn main:app --reload --host 0.0.0.0
```

## Running the model
1. After running the container, you will directly drop into the PIR_SGAN/sgan directory
2. To run the model on the custom.txt input file in datasets/eth/test/, run the following code:
3. **You don't need to run this if you are running the server**
```
python3.7 scripts/em2.py --model_path models/sgan-models/
```

## Running the simulations
Open the index.html file in chrome browser, the simulation should start automatically.


## Future work
