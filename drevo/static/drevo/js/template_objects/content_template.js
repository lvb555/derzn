let edit_menu = document.querySelector(".edit-menu") // меню создания-редактирования переменной
let action_type = document.querySelector(".edit-menu #action") // поле формы, отвечающее за тип действия (создать/редактировать)
let message = document.querySelector(".edit-menu__log")
let editing_var = null // id редактируемой переменной
let editing_turple = null // id редактируемого справочника
let action = null //
let subscription_field = document.querySelector("#subscription") // чекбокс "прописью"
let turple_field = document.querySelector("#turple") // поле выбора справочника
let connected_to_field = document.querySelector("#connected-to")
let main_checkbox = document.querySelector("#main input")
let turple_menu_btns = document.querySelectorAll(".turple-selection-btns .turple-selection__btn")
let url = window.location.href.split("document-template")[0] + "document-template"
let csrftoken = getCookie("csrftoken")
let types_block = document.querySelector("#type_of") // блок с полем выбора типа содержимого 
let type = document.querySelector("#type_of select") // поле выбора типа содержимого
let types = { // допустимые типы содержимого
	"text": 0,
	"number": 1,
	"date": 2
}

let structure = document.querySelector("#structure select") // поле выбора структуры объекта
let structure_types = {} // допустимые типы содержимого
new Array("var", "arr", "turple", "iterator", "if").forEach((i, index) => {
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
	body.append("is_global", form.querySelector("#id_is_global").checked)
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
		} else if(i.type === "checkbox" && i.checked) {
			body.append(i.name, true)
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

	if (!edit_menu.classList.contains("edit-menu_show")) {
		message.innerHTML = ""
		action = "edit"	
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

		edit_menu.classList.add("edit-menu_show")
	}
}


function update_state(e) {
	// обновить форму

	is_turple_or_control = [structure_types["iterator"], structure_types["turple"], structure_types["if"]].includes(Number(structure.value))
	subscription_field.style.display = type.value == types["text"] || is_turple_or_control ? "none" : "block"
	types_block.style.display = is_turple_or_control ? "none" : "block"
	connected_to_field.style.display = main_checkbox.checked || is_turple_or_control ? "none" : "block"
	main_checkbox.parentElement.style.display = is_turple_or_control ? "none" : "block"
	turple_field.style.display = structure.value == structure_types["turple"] ? "block" : "none"
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

document.querySelector("#structure select").addEventListener("change", update_state)


// изменили тип значения
document.querySelector("#type_of select").addEventListener("change", update_state)


// открыть форму для создания
document.querySelector(".objects__create_btn").addEventListener("click", async (e) => {
	if (!edit_menu.classList.contains("edit_menu_show")) {

		document.querySelectorAll(".edit-menu > .field input, .edit-menu > .field select").forEach((i) => {
			if (i.type == "checkbox" || i.type == "radio") {
				i.checked = false
			} else {
				i.value = ""
			}
		})

		update_state(e)
		edit_menu.classList.add("edit-menu_show")
	}
})


// открыть форму для создания
document.querySelector(".objects__create_btn").addEventListener("click", async (e) => {
	if (!edit_menu.classList.contains("edit_menu_show")) {
		action = "create"
		editing_var = null
		message.innerHTML = ""
	}
})


// закрытие формы
document.querySelector(".edit-menu__close-btn").addEventListener("click", (e) => {
	if (edit_menu.classList.contains("edit-menu_show")) {
		update_state(e)
		edit_menu.classList.remove("edit-menu_show")
	}
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
		console.log(ans)
		if (ans["res"] == "ok") {
			let blocks = document.querySelector(".objects__body")
			let clone = document.querySelector(".objects-list__object-card.clone")

			blocks.querySelectorAll(".objects__objects-list").forEach((i) => {
				while (i.firstChild) {
					i.removeChild(i.firstChild)
				}
			})

			ans["objects"].forEach((i) => {
				let obj = clone.cloneNode(true)
				obj.setAttribute("id", `pk-${i["pk"]}`)
				obj.querySelector(".object-card__header").innerHTML = i["fields"]["name"]
				obj.classList.remove("clone")
				obj.style.display = "inline-block"
				obj.querySelector(".object-card__btn.edit").addEventListener("click", edit_var_foo)
				blocks.querySelector(`#structure-${i["fields"]["structure"]}`).appendChild(obj)
			})

		} else {
			message.innerHTML = ans["errors"]["__all__"]
		}
	})
})


// создание нового словаря
document.querySelector(".turple-form__save-btn").addEventListener('click', (e) => {
	console.log(url + "/turple_processing")
	let body = TurpleProcessingBody()
	console.log(body)

	fetch(url + "/turple_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		console.log(ans)

		let turple_select = document.querySelector('.turple-selection__field select')
		while (turple_select.firstChild) {
			turple_select.removeChild(turple_select.firstChild)
		}

		ans["turples"].forEach((i) => {
			let option = document.createElement("option")
			option.value = i["pk"]
			option.innerHTML = i["fields"]["name"]

			turple_select.appendChild(option)
		})
		let option = document.createElement("option")
		option.value = ""
		option.innerHTML = "Новый словарь"
		option.setAttribute("checked", true)
		turple_select.value = ""
	})
})


// открыть форму для создания справочника
document.querySelector(".turple-selection__btn.create").addEventListener("click", (e) => {
	editing_turple = null
	let form = document.querySelector(".turple-form")
	form.querySelector("#id_name").value = ""
	form.querySelector("#id_is_global").checked = false
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
	form.querySelector("#id_is_global").checked = false
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
		form.querySelector("#id_is_global").checked = ans["turple"]["is_global"]
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