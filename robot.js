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

	display() {
		let c = color(this.color);
		fill(c);
		noStroke();
		circle(this.posX, this.posY, 5);
	}
}
