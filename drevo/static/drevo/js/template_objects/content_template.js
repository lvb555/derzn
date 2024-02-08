let edit_menu = document.querySelector(".edit-menu") // меню создания-редактирования переменной
let message_block = document.querySelector(".edit-menu__log-container")
let editing_var = null // id редактируемой переменной
let editing_turple = null // id редактируемого справочника
let edit_menu_title = document.querySelector("#ObjectModal .modal-title")
let action = null //
let subscription_field = document.querySelector("#subscription") // чекбокс "прописью"
let turple_field = document.querySelector("#turple") // поле выбора справочника
let connected_to_field = document.querySelector("#connected-to")
let main_checkbox = document.querySelector("#main input")
let turple_menu_btns = document.querySelectorAll(".turple-selection-btns .turple-selection__btn")
let url = window.location.href.split("document-template")[0] + "document-template"
let csrftoken = getCookie("csrftoken")
let type = document.querySelector("#type_of select") // поле выбора типа содержимого
let types = { // допустимые типы содержимого
	"text": 0,
	"number": 1,
	"date": 2,
	"tuple": 3
}

let structure = document.querySelector("#structure input") // поле выбора структуры объекта
let structure_types = {} // допустимые типы содержимого
new Array("var", "arr", "iterator", "if").forEach((i, index) => {
	structure_types[i] = index
})


function stripQueryParam(path) { 
	// обрезание параметров запроса из url адреса
	return path.slice(0, path.indexOf("?"))
}


function TurpleEditID() {
	// собрать тело для запроса данных редактируемого справочника

	let body = new FormData()
	body.append("id", document.querySelector(".field#turple select").value)
	return body
}


function TurpleProcessingBody() {
	// собрать тело для запроса создания/изменения справочника

	let form = document.querySelector(".turple-form")
	let body = new FormData()

	if (editing_turple !== null) {
		body.append("id", editing_turple)
	}
	body.append("name", form.querySelector("#id_name").value)
	body.append("availability", form.querySelector("#id_availability_0[checked], #id_availability_1[checked]").value)
	body.append("weight", form.querySelector("#id_weight").value)
	body.append("knowledge", form.querySelector("#id_knowledge").value)

	document.querySelectorAll(".turple-menu__element").forEach((i) => {
		i.querySelectorAll("input, select").forEach((j) => {
			body.append(j.name, j.value)
		})
	})

	return body
}


function ObjectProcessingBody (action) {
	// собрать тело для запроса создания/редактирования объекта

	body = new FormData()
	document.querySelectorAll(".edit-menu > .field input").forEach((i) => {

		console.log(i)

		if (i.type !== "checkbox" && i.type !== "radio"){
			body.append(i.name, i.value)
		} else if(i.type === "checkbox") {
			body.append(i.name, i.checked)
		} else if(i.checked) {
			body.append(i.name, i.value)
		}
	})

	edit_menu.querySelectorAll(".edit-menu > .field select").forEach((i) => {
		body.append(i.name, i.value)
	})

	edit_menu.querySelectorAll(".edit-menu > .field textarea").forEach((i) => {
		body.append(i.name, i.innerHTML)
	})

	body.append("action", action)
	body.append("knowledge", document.querySelector("#document_pk").value)

	if (editing_var !== null) {
		body.append("pk", editing_var)	
	}

	return body
}


function stripPrimaryKey(str) {
	return Number(str.split("-")[1])
}


function getCookie(name) {
	//получить нужный параметр из куки
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function edit_var_foo(e) {
	// открыть форму для редактирования объекта
	action = "edit"	
	edit_menu_title.innerHTML = "Редактирование объекта шаблона"
	editing_var = stripPrimaryKey(e.target.closest(".objects-list__object-card").id)
	update_state(e)

	fetch(url + `/document_object_processing?id=${editing_var}`, {"method": "get", "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		if (ans["res"] !== "ok")
			return
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


function update_state(e) {
	// обновить форму
	console.log(types.value)
	is_turple = type.value == types["tuple"]
	subscription_field.style.display = type.value == types["text"] || is_turple ? "none" : "block"
	// connected_to_field.style.display = main_checkbox.checked || is_turple ? "none" : "block"
	// main_checkbox.parentElement.style.display = is_turple ? "none" : "block"
	turple_field.style.display = type.value == types["tuple"] ? "block" : "none"
	if (turple_field.querySelector("select").value === "") {
		turple_menu_btns[1].style.display = "none"
		turple_menu_btns[2].style.display = "none"
	} else {
		turple_menu_btns[1].style.display = "inline-block"
		turple_menu_btns[2].style.display = "inline-block"
	}
}


function getCookie(name) {
	//получить нужный параметр из куки

    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


const csrftoken2 = getCookie('csrftoken')

main_checkbox.addEventListener("change", update_state)

document.querySelector("#structure input").addEventListener("change", update_state)


// изменили тип значения
document.querySelector("#type_of select").addEventListener("change", update_state)


// открыть форму для создания
document.querySelector(".objects__create_btn").addEventListener("click", (e) => {
	edit_menu_title.innerHTML = "Создание объекта шаблона"
	action = "create"
	editing_var = null
	document.querySelectorAll(".edit-menu > .field input, .edit-menu > .field select").forEach((i) => {
		if (i.type == "checkbox" || i.type == "radio") {
			i.checked = false
		} else {
			i.value = ""
		}
	})

	update_state(e)
})

// селектор словаря
document.querySelector(".turple-selection__field select").addEventListener("change", update_state)


// открыть форму для редактирования переменной
document.querySelectorAll(".object-card__btn.edit").forEach((i) => {
	i.addEventListener("click", edit_var_foo)
})


// отправка формы
document.querySelector(".edit-menu__save-btn").addEventListener("click", (e) => {
	let body = ObjectProcessingBody(action)
	
	console.log(body)

	fetch(url + "/document_object_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		let message = document.createElement("p")
		message.classList.add("edit-menu__log")
		console.log(ans)
		if (ans["res"] == "ok") {
			let blocks = document.querySelector(".objects__body")
			let clone = document.querySelector(".objects-list__object-card.clone")
			let select = connected_to_field.querySelector("select")

			blocks.querySelectorAll(".objects__objects-list").forEach((i) => {
				while (i.firstChild) {
					i.removeChild(i.firstChild)
				}
			})

			while(select.firstChild) {
				select.removeChild(select.firstChild)
			}

			let default_option = document.createElement("option")
			default_option.value = ""
			default_option.innerHTML = "Без подчинения"
			default_option.selected = true
			select.appendChild(default_option)
			select.value = ""

			ans["objects"].forEach((i) => {
				let obj = clone.cloneNode(true)
				obj.setAttribute("id", `pk-${i["pk"]}`)
				obj.querySelector(".object-card__header").innerHTML = i["fields"]["name"]
				obj.classList.remove("clone")
				obj.style.display = "inline-block"
				obj.querySelector(".object-card__btn.edit").addEventListener("click", edit_var_foo)
				blocks.querySelector(`#structure-${i["fields"]["structure"]}`).appendChild(obj)

				if (i["fields"]["is_main"]) {
					let option = document.createElement("option")
					option.value = i["pk"]
					option.innerHTML = i["fields"]["name"]
					select.appendChild(option)
					if (option.value === body.get("connected_to")) {
						option.selected = true
						default_option.selected = false
					}
				}
			})



			message.innerHTML = (action === "edit" ? "Изменения сохранены" : "Объект создан")

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


// создание нового справочника
document.querySelector(".turple-form__save-btn").addEventListener('click', (e) => {
	console.log(url + "/turple_processing")
	let body = TurpleProcessingBody()
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
	form.querySelector("#id_availability_0").checked = false
	form.querySelector("#id_availability_1").checked = false
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

	let select = document.querySelector(".element-form #id_var").cloneNode(true)
	select.setAttribute("name", "element-var")
	select.value = document.querySelector(".element-form #id_var").value

	object.appendChild(name)
	object.appendChild(select)
	object.appendChild(weight)
	object.appendChild(id)
	elements_block.append(object)
})