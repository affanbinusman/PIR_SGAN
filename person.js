class Person {

	constructor(startX, startY, mX, mY, color) {
		this.posX = startX;
		this.posY = startY;

		this.mX = mX;
		this.mY = mY;

		this.color = color;
	}

	updatePosition(updatePositionsHard, posX=1, posY=1) {

		if (updatePositionsHard) {
			this.posX = posX;
			this.posY = posY;
		}
		else {
			this.posX += this.mX;
			this.posY += this.mY;
		}
		
	}

	display() {
		let c = color(this.color);
		fill(c);
		noStroke();
		rect(this.posX, this.posY, 10, 10);
	}
}
