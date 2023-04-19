var persons = [];
var robot;

var rtrajs = [];
var rpath = [];

var ptrajs = [];
var predictions = [];
var plist = []

var timestep = 0;

const numberOfPeople = 10;
const radius = 50;

function getNewPredictions() {

	const data = {
		"numberOfPeople": numberOfPeople,
		"radius": radius,
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
		console.log(data)
		if (data.res == 0) {
			ptrajs = [];
			predictions = [];
			plist = [];
		}
		else {
			predictions = data.preds;
			plist = data.plist;
		}
		//loop();
	});
}


function setRobotGoalPosition() {
	const data = {
		"goalX": robot.goalX,
		"goalY": robot.goalY
	};
	
	fetch("http://localhost:8000/set_goal", {
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
		console.log(data)
	});
}



function getRobotPositions() {
	const data = {
		"ptrajs":ptrajs,
		"predictions":predictions,
		"rtrajs": rtrajs
	};
	
	fetch("http://localhost:8000/get_robot", {
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
		console.log(data)
		rpath = data.rpath;	
		loop();
	});
}


function setup() {
	createCanvas(400, 400);
	frameRate(1);

	// create robot
	let startX = random(100, 300);
	let startY = random(100, 300);
	let goalX = 400 - startX;
	let goalY = 400 - startY;
	robot = new Robot(startX, startY, goalX, goalY);

	for (let i  = 0; i < numberOfPeople; i++) {
		persons.push(new Person(randomGaussian(200, 50), randomGaussian(200, 50),
									randomGaussian(0), randomGaussian(0)));
	}

	setRobotGoalPosition();
}

function draw() {
	background(0);
	
	if (rpath.length > 0) {
		robot.updatePosition(rpath[0][0], rpath[0][1]);
		rpath.shift();
	}
	robot.display()
	rtrajs.push([timestep, 0, robot.posX, robot.posY]);

	if (rtrajs.length > 8)
		rtrajs.shift();

	let pidx = 0;
	for (let i = 0; i < numberOfPeople; i++) {
		if (predictions.length != 0 && i == plist[pidx]) {
			persons[i].updatePosition(1, predictions[0][pidx+1][0], predictions[0][pidx+1][1]);
			pidx += 1;
		}
		else {
			persons[i].updatePosition(0);
		}
		persons[i].display();
		
		ptrajs.push([timestep, i, persons[i].posX, persons[i].posY]);

		if (ptrajs.length > (persons.length * 8)) {
			ptrajs.shift();
		}
	}

	predictions.shift();
	console.log(predictions)

	if (ptrajs.length >= (numberOfPeople * 8) &&
		predictions.length == 0) {
		getNewPredictions();
		getRobotPositions();
		noLoop();
	} 


	timestep += 10;
}
