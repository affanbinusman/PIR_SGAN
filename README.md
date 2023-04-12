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
docker run . --platform=linux/amd64 -p 8000:8000 -it sgan
```

## Running the model
1. After running the container, you will directly drop into the PIR_SGAN/sgan directory
2. To run the model on the custom.txt input file in datasets/eth/test/, run the following code:
```
python3.7 scripts/em2.py --model_path models/sgan-models/
```

## Running the FastAPI based server
```
uvicorn main:app --reload --host 0.0.0.0
```

## Future work
1. Integrate FastAPI server for taking the observations and giving a predicted path
2. Create a p5.js based frontend for simulating the people and the bots
3. Autorun the server 

@affanbinusman
1. Change dict to nparray /Users/affanbinusman/Documents/GitHub/PIR_SGAN/sgan/sgan/data/trajectories.py