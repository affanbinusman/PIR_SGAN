let posX = 0;
let posY = 0;


function getNewPredictions() {
		const data = { msg: "Hello world!" };
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
		createCanvas(800, 800);
		frameRate(10);
}

function draw() {
		background(0);

		rect(posX, posY, 10, 10);

		posX += 1;
		posY += 1;

		setInterval(getNewPredictions, 2000);

}
