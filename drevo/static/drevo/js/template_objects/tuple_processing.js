import {TurpleProcessingBody, csrftoken} from "./setup_queries.js"

let editing_turple = null // id редактируемого справочника
const url = window.location.href.split("document-template")[0] + "document-template"


// создание нового справочника
document.querySelector(".turple-form__save-btn").addEventListener('click', (e) => {
	console.log(url + "/turple_processing")
	let body = TurpleProcessingBody(editing_turple)
	console.log(body)

	fetch(url + "/turple_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		console.log(ans)
		let message = document.createElement("p")
		message.classList.add("edit-menu__log")
		if (ans["res"] === "ok") {
			let a = (body.has("id") ? body.get("id") : null)
			let turple_select = document.querySelector('.turple-selection__field select')
			while (turple_select.firstChild) {
				turple_select.removeChild(turple_select.firstChild)
			}

			let default_option = document.createElement("option")
			default_option.value = ""
			default_option.innerHTML = "Новый справочник"
			turple_select.appendChild(default_option)
			default_option.selected = true

			ans["turples"].forEach((i) => {
				let option = document.createElement("option")
				option.value = i["pk"]
				option.innerHTML = i["fields"]["name"]
				turple_select.appendChild(option)
				if (i["pk"] === a) {
					default_option.selected = false
					option.selected = true
				}
			})	
			if (body.has("id"))
				message.innerHTML = "Изменения сохранены"
			else
				message.innerHTML = "Справочник создан"
		} else if (ans["res"] == "validation error") {
			message.innerHTML = "Что-то пошло не так"
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


// открыть форму для создания справочника
document.querySelector(".turple-selection__btn.create").addEventListener("click", (e) => {
	editing_turple = null
	let form = document.querySelector(".turple-form")
	form.querySelector("#id_name").value = ""
	form.querySelector("#id_weight").value = 100
	let elements_block = document.querySelector(".turple-menu__objects-list")
	while (elements_block.firstChild) {
		elements_block.removeChild(elements_block.firstChild)
	}
})


// открыть форму для редактирования справочника
document.querySelector(".turple-selection__btn.edit").addEventListener("click", (e) => {
	let form = document.querySelector(".turple-form")
	form.querySelector("#id_name").value = ""
	form.querySelector("#id_availability_0").checked = false
	form.querySelector("#id_availability_1").checked = false
	form.querySelector("#id_weight").value = 100
	let elements_block = document.querySelector(".turple-menu__objects-list")
	while (elements_block.firstChild) {
		elements_block.removeChild(elements_block.firstChild)
	}

	editing_turple = TurpleEditID().get('id')

	fetch(url + `/turple_processing?id=${editing_turple}`, {"method": "get", "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		console.log(ans)

		form.querySelector("#id_name").value = ans["turple"]["name"]
		form.querySelector("#id_availability_0").checked = ans["turple"]["availability"] === 0
		form.querySelector("#id_availability_1").checked = ans["turple"]["availability"] === 1
		form.querySelector("#id_weight").value = ans["turple"]["weight"]

		
		
		ans["elements"].forEach((i) => {
			let object = document.createElement("div")
			object.classList.add("object", "turple-menu__element")

			let name = document.createElement("input")
			name.classList.add("form-control")
			name.setAttribute("name", "element-name")
			name.setAttribute("type", "text")
			name.value = i["fields"]["value"]

			let id = document.createElement("input") 
			id.setAttribute("type", "hidden")
			id.setAttribute("name", "element-id")
			id.value = i["pk"]

			let weight = document.createElement("input")
			weight.setAttribute("type", "number")
			weight.setAttribute("name", "element-weight")
			weight.classList.add("form-control")
			weight.value = i["fields"]["weight"]

			let select = document.querySelector(".element-form #id_var").cloneNode(true)
			select.value = i["fields"]["var"] === null ? "" : i["fields"]["var"]
			select.setAttribute("name", "element-var")

			object.appendChild(name)
			object.appendChild(select)
			object.appendChild(weight)
			object.appendChild(id)
			elements_block.append(object)
		})
	})
})

// создания нового элемента справочника
document.querySelector(".element-form__save-btn").addEventListener("click", (e) => {
	let elements_block = document.querySelector(".turple-menu__objects-list")
	let object = document.createElement("div")
	object.classList.add("object", "turple-menu__element")

	let name = document.createElement("input")
	name.classList.add("form-control")
	name.setAttribute("name", "element-name")
	name.setAttribute("type", "text")
	name.value = document.querySelector(".element-form #id_value").value

	let id = document.createElement("input")
	id.setAttribute("name", "element-id")
	id.setAttribute("type", "hidden")
	id.value = ""

	let weight = document.createElement("input")
	weight.setAttribute("type", "number")
	weight.setAttribute("name", "element-weight")
	weight.classList.add("form-control")
	weight.value = document.querySelector(".element-form #id_weight").value

	object.appendChild(name)
	object.appendChild(weight)
	object.appendChild(id)
	elements_block.append(object)
})