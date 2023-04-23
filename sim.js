var persons = [];
var robot;

var rtrajs = [];
var rpath = [];
var robot_result = true;

var ptrajs = [];
var predictions = [];
var pred_result = true
var plist = []

let loopStep = 0;
var timestep = 0;

const numberOfPeople = 3;
const radius = 50;

async function getNewPredictions() {
	//noLoop();
	const data = {
		"numberOfPeople": numberOfPeople,
		"radius": radius,
		"ptrajs": ptrajs,
		"rtrajs": rtrajs
	};

	console.log("rtrajs.length = ", rtrajs.length)


	const xhr = new XMLHttpRequest();

	xhr.open("POST", 'http://localhost:8000/get_preds', false);
	xhr.setRequestHeader('Content-Type', 'application/json');

	xhr.send(JSON.stringify(data));

	if (xhr.status == 200) {
		const res = xhr.responseText;
		console.log(res);
		const preds = JSON.parse(res);
		if (preds.res == 0) {
			ptrajs = [];
			predictions = [];
			plist = [];
		}
		else {
			predictions = preds.preds;
			plist = preds.plist;
		}

		pred_result = true;
	}

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
	// create array to store next 8 positions of all people
//	[
//		[0, 0], //p1
//		[1, 1], //p2
//		[2, 2], //p3
//		[0, 1], //p1
//	]
	let ppath = []

	let idx = 0;
	for (let t = 0; t < 8; t++) {
		idx = 0;
		for(let p = 0; p < numberOfPeople; p++) {
			if (predictions.length != 0 && p == plist[idx]) {
				ppath.push([predictions[t][idx+1][0], predictions[t][idx+1][1]]);
				idx++;
			}
			else {
				px = persons[p].posX + persons[p].mX * (t + 1);
				py = persons[p].posY + persons[p].mY * (t + 1);
				ppath.push([px, py]);
			}
		}
	}

	console.log(ppath)


	const data = {
		"numberOfPeople":numberOfPeople,
		"ppath":ppath,
		"rtrajs": rtrajs
	};
	
	const xhr = new XMLHttpRequest();

	xhr.open("POST", 'http://localhost:8000/get_robot', false);
	xhr.setRequestHeader('Content-Type', 'application/json');

	xhr.send(JSON.stringify(data));

	if (xhr.status == 200) {
		const res = xhr.responseText;
		const preds = JSON.parse(res);
		console.log(preds);
		rpath = preds.rpath;
		console.log(rpath)
		robot_result = true;
//		const obstacles = preds.obstacles;
//
//		for (let i = 0; i < obstacles.length; i++) {
//			push();
//			fill(255);
//			noStroke();
//			circle(obstacles[i][0], obstacles[i][1], obstacles[i][2]);
//			pop();
//		}
	}
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

	if (!robot_result || !pred_result)
		return;

	background(0);

	if (rpath.length > 0) {
		console.log(rpath[0][0][0])
		console.log(rpath[0][0][1])
		robot.updatePosition(rpath[0][0][0], rpath[0][0][1]);
		rpath.shift();
	}
	robot.display();
	robot.displayGoal();
	rtrajs.push([timestep, 0, robot.posX, robot.posY]);

	if (rtrajs.length > 8)
		rtrajs.shift();

	let pidx = 0;
	for (let i = 0; i < numberOfPeople; i++) {
		if (predictions.length != 0 && (i+1) == plist[pidx]) {
			persons[i].updatePosition(1, predictions[0][pidx+1][0], predictions[0][pidx+1][1]);
			pidx += 1;
		}
		else {
			persons[i].updatePosition(0);
		}
		persons[i].display();
		
		ptrajs.push([timestep, i+1, persons[i].posX, persons[i].posY]);

		if (ptrajs.length > (persons.length * 8)) {
			ptrajs.shift();
		}
	}

	predictions.shift();
	console.log(predictions)

	if (loopStep > 7 &&
		predictions.length == 0) {
		pred_result = false;
		robot_result = false;
		getNewPredictions();
		getRobotPositions();
		loopStep = 0;
	}

//	debugger;


	timestep += 10;
	loopStep += 1;
}
