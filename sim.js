var persons = [];
var robot;

var rtrajs = [];
var rpath = [];

var ptrajs = [];
var predictions = [];

var timestep = 0;
const numberOfPeople = 2;

function getNewPredictions() {

	const data = {
		"numberOfPeople": numberOfPeople,
		"ptrajs": ptrajs, 
		"rtrajs": rtrajs
	};
	
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
		predictions = data.preds;
		if (data.preds == 0) 
			ptrajs = [];
		loop();
	});
}


function setup() {
	createCanvas(400, 400);
	frameRate(1);

	// create robot
	let startX = random(400);
	let startY = random(400);
	let goalX = 400 - startX;
	let goalY = 400 - startY;
	robot = new Robot(startX, startY, goalX, goalY);

	for (let i  = 0; i < numberOfPeople; i++) {
		persons.push(new Person(randomGaussian(200, 50), randomGaussian(200, 50),
									randomGaussian(0), randomGaussian(0)));
	}

}

function draw() {
	background(0);

	robot.display()
	rtrajs.push([timestep, 0, robot.posX, robot.posY]);

	if (rtrajs.length > 8)
		rtrajs.shift();

	for (let i = 0; i < numberOfPeople; i++) {
		if (predictions.length != 0) {
			persons[i].updatePosition(1, predictions[0][i][0], predictions[0][i][1]);
		}
		else {
			persons[i].updatePosition(0);
		}
		persons[i].display();
		
		ptrajs.push([timestep, i + 1, persons[i].posX, persons[i].posY]);

		if (ptrajs.length > (persons.length * 8)) {
			ptrajs.shift();
		}
	}

	predictions.shift();
	console.log(predictions)

	if (ptrajs.length >= (numberOfPeople * 8) &&
		predictions.length == 0) {
		getNewPredictions();
		noLoop();
	} 


	timestep += 10;
}
