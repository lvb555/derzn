let countOfSelected = 0
let isCtrlPressed = false

document.addEventListener("DOMContentLoaded", (event) => {
	let selectObject = document.querySelector("#id_available_suggestion_types")
	let selectOptions = selectObject.querySelectorAll("option")

	selectOptions.forEach((i) => {
		countOfSelected += i.selected
		i.addEventListener("click", (e) => {
			console.log("click")
			if (e.target.selected)
				countOfSelected++
			else
				countOfSelected--

			if (countOfSelected > 0 && !selectObject.classList.contains("blocked") && !isCtrlPressed)
				selectObject.classList.add("blocked")
		})
	})

	console.log(selectObject)
	document.addEventListener("keydown", (e) => {
		console.log(e.code)
		if (e.code === "ControlLeft" || e.code === "ControlRight") {
			isCtrlPressed = true
			if (selectObject.classList.contains("blocked"))
				selectObject.classList.remove("blocked")
		}
	})

	document.addEventListener("keyup", (e) => {
		console.log(e.code)
		if (e.code === "ControlLeft" || e.code === "ControlRight") {
			isCtrlPressed = false
			if (!selectObject.classList.contains("blocked") && countOfSelected > 0)
				selectObject.classList.add("blocked")
		}
	})
})

