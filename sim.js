var persons = [];
var robot;

var rtrajs = [];
var rpath = [];

var ptrajs = [];
var predictions = [];
var pred_result = true
var plist = []

let loopStep = 0;
var timestep = 0;

const numberOfPeople = 3;
const radius = 50;

function getNewPredictions() {
	noLoop();
	const data = {
		"numberOfPeople": numberOfPeople,
		"radius": radius,
		"ptrajs": ptrajs,
		"rtrajs": rtrajs
	};

	console.log("rtrajs.length = ", rtrajs.length)
	
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
		if (data.res == 0) {
			ptrajs = [];
			predictions = [];
			plist = [];
		}
		else {
			predictions = data.preds;
			plist = data.plist;
		}
		getRobotPositions();
		//loop();
	});
}


function setRobotGoalPosition() {
	const data = {
		"startX": robot.posX,
		"startY": robot.posY,
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
	noLoop();	
	// create array to store next 8 positions of all people
	let ppath = []

	let idx = 0;
	for (let i = 0; i < numberOfPeople; i++) {
		let px = persons[i].posX;
		let py = persons[i].posY;
		for (let j = 0; j < 8; j++) {
			if (predictions.length != 0 && i == idx) {
				ppath.push([i, predictions[j][idx+1][0], predictions[j][idx+1][1]]);
			}
			else {
				px += persons[i].mX;
				py += persons[i].mY;
				ppath.push([i, px, py]);
			}
		}
		idx++;
	}

	const data = {
		"numberOfPeople":numberOfPeople,
		"ppath":ppath,
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
		console.log(rpath)
		loop();
	});
}


function setup() {
	createCanvas(400, 400);
	frameRate(1);

	// create robot
	let startX = random(100, 300);
	let startY = random(100, 300);
	let goalX = startX + random(-50, 50);
	let goalY = goalX + random(-50, 50);
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
		console.log(rpath[0][0][0])
		console.log(rpath[0][0][1])
		robot.updatePosition(rpath[0][0][0], rpath[0][0][1]);
		rpath.shift();
	}
	robot.display();
	robot.displayGoal();
	rtrajs.push([timestep, numberOfPeople + 1, robot.posX, robot.posY]);

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

	if (loopStep == 7 &&
		predictions.length == 0) {
		pred_result = false;
		getNewPredictions();
		noLoop();
//		getRobotPositions();
//		noLoop();
		loopStep = 0;
	} 


	timestep += 10;
	loopStep += 1;
}
