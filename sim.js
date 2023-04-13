var persons = [];
var trajectories = [];
var predictions = [];
var timestep = 0;

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
			console.log(data);
	});
}


function setup() {
	createCanvas(400, 400);
	frameRate(10);

	persons.push(new Person(0, 0, 1, 1, "red"));
	persons.push(new Person(350, 350, -1, -1, "blue"));
}

function draw() {
	background(0);

	for (let i = 0; i < 2; i++) {
		persons[i].updatePosition(0);
		persons[i].display();
		
		trajectories.push([timestep, i, persons[i].posX, persons[i].posY]);

		if (trajectories.length > (persons.length * 8)) {
			trajectories.shift();
		}

	}

	if (trajectories.length >= (persons.length * 8)) {
		getNewPredictions();
	} 


	timestep += 10;
}
