var persons = [];
var trajectories = [];
var predictions = [];
var timestep = 0;
var requestMade = false;
const numberOfPeople = 2;

function getNewPredictions() {
	const data = {"data": trajectories};
	fetch("http://localhost:8000/get_preds", {
			method: 'POST',
			headers: {
					'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
	})
	.then(response => {
			if (response.ok) {
					return response.json();
			}
			else {
					throw new Error("barf!");
			}
	})
	.then(data => {
			requestMade = false;
			predictions = data.preds;
			loop();
	});
}


function setup() {
	createCanvas(400, 400);
	frameRate(1);

	for (let i  = 0; i < numberOfPeople; i++) {
		persons.push(new Person(randomGaussian(200, 50), randomGaussian(200, 50),
									randomGaussian(0), randomGaussian(0)));
	}

	// persons.push(new Person(75, 75, 1, 1));
	// persons.push(new Person(125, 125, -1, -1));
}

function draw() {
	background(0);


	for (let i = 0; i < numberOfPeople; i++) {
		if (predictions.length != 0) {
			persons[i].updatePosition(1, predictions[0][i][0], predictions[0][i][1]);
		}
		else {
			persons[i].updatePosition(0);
		}
		persons[i].display();
		
		trajectories.push([timestep, i, persons[i].posX, persons[i].posY]);

		if (trajectories.length > (persons.length * 8)) {
			trajectories.shift();
		}
	}

	predictions.shift();
	console.log(predictions)

	if (trajectories.length >= (persons.length * 8) &&
		predictions.length == 0) {
		getNewPredictions();
		noLoop();
	} 


	timestep += 10;
}
