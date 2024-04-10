import {csrftoken} from "./setup_queries.js"

const zn_pk = document.querySelector(".template #document_pk").value
const pk = document.querySelector(".template #id_pk").value
const message_block = document.querySelector(".log-container")

function SaveTemplateBody() {
	const body = new FormData()
	body.append("content", CKEDITOR.instances.id_content.getData())
	body.append("zn_pk", zn_pk)
	body.append("pk", pk)
	const objects = CKEDITOR.instances.id_content.document.$.querySelectorAll("span.template-object")
	let set = new Set()
	objects.forEach((i) => {
		set.add(i.id)
	})

	Array.from(set).forEach((i) => {
		body.append("objects", i)
	})

	return body
}

const url = window.location.href.split("document-template")[0] + "document-template/save-text-template"
const save_btn = document.querySelector(".template-btn.save")

document.addEventListener("DOMContentLoaded", (e) => {
	save_btn.addEventListener("click", (e) => {

		fetch(url, {"method":"post", "headers":{"X-CSRFToken":csrftoken}, "body": SaveTemplateBody()})
		.then(res => res.json())
		.then((ans) => {

			let message = document.createElement("p")
			message.classList.add("log-container__log")

			if (ans["res"] == "ok") {
				message.innerHTML = "Изменения сохранены"
			} else if (ans["res"] === "err") {
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
})