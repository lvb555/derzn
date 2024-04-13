import {ObjectProcessingBody} from "./setup_queries.js"
import {csrftoken} from "./setup_queries.js"
import {update_state} from "./dynamic_form.js"

let editing_var = null // id редактируемой переменной
let action = null
const edit_menu_title = document.querySelector("#ObjectModal .modal-title")
const url = window.location.href.split("document-template")[0] + "document-template"
const connected_to_block = document.querySelector("#connected-to")
const message_block = document.querySelector(".log-container")

const focused_object = document.querySelector(".object-card")
const focused_object_header = document.querySelector(".object-card__header")


function edit_var_foo(e) {
	// открыть форму для редактирования объекта
	action = "edit"	
	edit_menu_title.innerHTML = "Редактирование объекта шаблона"
	editing_var = e.target.closest(".template__selected-object").id

	fetch(url + `/document_object_processing?id=${editing_var}`, {"method": "get", "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		if (ans["res"] !== "ok") {
			console.log(ans)
			return
		}
		document.querySelectorAll(".edit-menu > .field input, .edit-menu > .field select").forEach((i) => {
			if (i.type == "checkbox") {
				i.checked = ans["object"][i.name]
			} else if (i.type == "radio") {
				i.checked = i.value == ans["object"][i.name]
			} else {
				i.value = ans["object"][i.name] !== null ? ans["object"][i.name] : ""
			}
		})
		document.querySelector(".edit-menu textarea").value = ans["object"]["fill_title"]
	})
	.then(() => {
		update_state(e)
	})
}


// открыть форму для редактирования переменной
document.querySelectorAll(".object-card__btn.edit").forEach((i) => {
	i.addEventListener("click", edit_var_foo)
})


// открыть форму для создания
// document.querySelector(".template__template-actions .template-btn.create").addEventListener("click", (e) => {
// 	edit_menu_title.innerHTML = "Создание объекта шаблона"
// 	action = "create"
// 	editing_var = null
// 	document.querySelectorAll(".edit-menu > .field input, .edit-menu > .field select").forEach((i) => {
// 		if (i.type == "checkbox" || i.type == "radio") {
// 			i.checked = false
// 		} else {
// 			i.value = ""
// 		}
// 	})

// 	update_state(e)
// })


// отправка формы
document.querySelector(".edit-menu__save-btn").addEventListener("click", (e) => {
	const body = ObjectProcessingBody(action, editing_var)
	

	fetch(url + "/document_object_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		let message = document.createElement("p")
		message.classList.add("log-container__log")
		console.log(ans)
		if (ans["res"] == "ok") {
			message.innerHTML = "Изменения сохранены"
		} else if (ans["res"] === "validation error") {
			message.innerHTML = ans["errors"]["__all__"][0]
		}
		message_block.insertBefore(message, message_block.firstChild)
		setTimeout(() => {
			message_block.style.display = "block"
			message.style.opacity = "100%"
				setTimeout(() => {
					message.style.opacity = "0%"
					setTimeout(() => {
						message_block.style.display = "none"
						message.remove()
					}, 510)
				}, 1500)
		}, 10)
	})
})


//удаление объекта
const span = document.querySelector("#delete-object-name")

document.querySelector(".object-card__btn.delete").addEventListener('click', (e) => {
	span.innerHTML = focused_object_header.innerHTML
})

document.querySelector("#DeleteObjectModal .btn:first-child").addEventListener('clicl', (e) => {
	
})
