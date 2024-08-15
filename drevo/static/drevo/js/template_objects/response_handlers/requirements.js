// Показать всплывающее сообщение пользователью с содержимым text.
export function show_message(text) {
	const message_block = document.querySelector(".log-container")
	const message = document.createElement("p")
	message.classList.add("log-container__log")
	message.innerHTML = text

	message_block.insertBefore(message, message_block.firstChild)
	setTimeout(() => {
		message_block.style.display = "block"
		message.style.opacity = "100%"
		setTimeout(() => {
			message.style.opacity = "0%"
			setTimeout(() => {
				message.remove()
				message_block.style.display = "none"
			}, 510)
		}, 3000)
	}, 10)
}

//найти объект с минимальным весом из objects, вес которого не меньше weight
export function FindNextElement(objects, weight) {
	let l = -1
	let r = objects.length
	while(r > l) {
		let w = Math.trunc((r + l) / 2)
		if (objects[w].dataset.weight >= weight) {
			r = w
		} else {
			l = w
		}
	}
	if (r == objects.length)
		return null
	return objects[r]
}