import {ObjectProcessingBody, GroupProcessingBody, csrftoken} from "./setup_queries.js"

const url = window.location.href.split("document-template")[0] + "document-template"
const message_block = document.querySelector(".log-container")

document.querySelectorAll(".node-name").forEach((i) => {
	i.addEventListener("dblclick", (e) => {
		const p = e.target.closest(".node-name")
		const object_name = p.querySelector("span").innerHTML
		const id = Number(p.id.split("-")[1])
		let availability = -1
		if (p.classList.contains("local"))
			availability = 0
		else if (p.classList.contains("global"))
			availability = 1
		else if (p.classList.contains("general"))
			availability = 2

		window.opener.postMessage(
			JSON.stringify({
				"name": object_name,
				"id": id,
				"availability": availability
			}),
			window.opener.location.href)
		window.close()
	})
})

document.querySelector(".edit-menu__save-btn").addEventListener('click', (e) => {
	let body
	if (e.target.closest("#ObjectModal"))
		body = ObjectProcessingBody("create", null)
	else
		body = GroupProcessingBody()

	console.log(body)

	fetch(url + "/document_object_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		let message = document.createElement("p")
		message.classList.add("log-container__log")
		console.log(ans)
		if (ans["res"] == "ok") {
			message.innerHTML = "Объект создан"
		} else if (ans["res"] === "validation error") {
			message.innerHTML = ans["errors"]["__all__"][0]
		}
		message_block.insertBefore(message, message_block.firstChild)
		setTimeout(() => {
			message.style.opacity = "100%"
			setTimeout(() => {
			message.style.opacity = "0%"
			setTimeout(() => {
				message.remove()
			}, 510)
		}, 1500)
		}, 10)
	})
})