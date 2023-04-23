class Robot {

	constructor(startX, startY, goalX, goalY) {
		this.posX = startX;
		this.posY = startY;

		this.goalX = goalX;
		this.goalY = goalY;

		this.color = color(random(255), random(255), random(255));

	}

	updatePosition(posX=1, posY=1) {
		this.posX = posX;
		this.posY = posY;
		
	}

	star(x, y, radius1, radius2, npoints) {
		let angle = TWO_PI / npoints;
		let halfAngle = angle / 2.0;
		beginShape();
		for (let a = 0; a < TWO_PI; a += angle) {
    		let sx = x + cos(a) * radius2;
			let sy = y + sin(a) * radius2;
    		vertex(sx, sy);
			sx = x + cos(a + halfAngle) * radius1;
    		sy = y + sin(a + halfAngle) * radius1;
    		vertex(sx, sy);
		}
		endShape(CLOSE);
	}

	display() {
		push();
		let c = color(this.color);
		fill(c);
		stroke(255);
		circle(this.posX, this.posY, 7);
		pop();
	}

	displayGoal() {
		push();
		let c = color(255);
		fill(c);
		noStroke();
		this.star(this.goalX, this.goalY, 3, 7, 5);
		pop();
	}
}
