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

export function FindNextElement(objects, weight) {
	let l = 0
	let r = objects.length
	while(r > l) {
		let w = Math.trunc((r + l) / 2)
		if (objects[w].dataset.weight >= weight) {
			r = w - 1
		} else {
			l = w + 1
		}
	}
	if (l == objects.length)
		return null
	return objects[l]
}