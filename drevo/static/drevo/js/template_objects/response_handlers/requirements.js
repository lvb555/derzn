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
		}, 1500)
	}, 10)
}