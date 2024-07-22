import {show_message} from "./requirements.js"
import {SelectObject, ExpandCollapseNodeChildren} from "../objects_tree.js"
import {ObjectInfoRequest} from "../requests/objects_tree.js"
import {SelecObjectToDelete} from "../objects_tree.js"

// В этом файле хранятся функции, меняющие DOM дерево в зависимости от ответа бекенда на запросы.
// со страницы drevo/znanie/<id>/document-template/object-select


// Добавляет новою вершину(лист) в дерево объектов. Вершина соответсвует новому объекту.
export function CreateNewObjec(ans) {
	const object_template = document.querySelector(".node.clone")

	if (ans["res"] == "ok") {
		const object = object_template.cloneNode(true)
		let parent
		if (ans["object"].connected_to) {
			parent = document.querySelector(`.node#id-${ans["object"].connected_to}`)
			if (parent.classList.contains("leaf")) {
				parent.classList.remove("leaf")
				const ul = document.createElement("ul")
				ul.classList.add("node-children")
				parent.appendChild(ul)
				parent = ul
			} else {
				parent = parent.querySelector(".node-children")
			}
			object.classList.add("child-node")
		} else {
			parent = document.querySelector(".objects-tree__containing-list")
		}
		if (ans["object"].is_main) {
			object.classList.add("group")
		} else {
			object.querySelector(".node-label__name").addEventListener("dblclick", SelectObject)
		}

		if (ans["object"].optional) {
			object.classList.add("optional")
		}
			
		object.classList.add("leaf")
		object.setAttribute("id", `id-${ans["object"].id}`)

		object.querySelector('.node-label__name span').innerHTML = (ans["object"].name)
		object.querySelector(".node__expand-btn").addEventListener("click", ExpandCollapseNodeChildren)
		object.querySelector(".node__collapse-btn").addEventListener("click", ExpandCollapseNodeChildren)
		object.querySelector(".node__actions .edit").addEventListener("click", ObjectInfoRequest)
		object.querySelector(".node__actions .delete").addEventListener("click", SelecObjectToDelete)
		object.classList.remove("clone")
		parent.appendChild(object)

		show_message("Объект создан")

	} else if (ans["res"] === "validation error") {
		show_message(ans["errors"]["__all__"][0])
	}
}

// Изменить дерево объектов в случае необходимости после редактирования объекта
export function UpdateTree(ans) {
	if (ans.res === "ok") {
		const object_node = document.querySelector(`.node#id-${ans.object.id}`)

		//обновить имя
		object_node.querySelector(".node-label__name > span").innerHTML = ans.object.name

		//Если сменился родитель объекта
		const object_parent_node = object_node.parentElement.closest(".node")
		if ((object_parent_node !== null ^ ans.object.connected_to !== null) || object_parent_node && (object_parent_node.id !== `id-${ans.object.connected_to}`)) {
			object_node.remove()
			if (object_parent_node && object_parent_node.querySelectorAll(".node").length == 0)
				object_parent_node.classList.add("leaf")
			if (ans.object.connected_to !== null) {
				let object_new_parent_node = document.querySelector(`.node#id-${ans.object.connected_to}`)
				object_new_parent_node.classList.remove("leaf")

				if (!object_new_parent_node.querySelector(".node-children")) {
					const ul = document.createElement("ul")
					ul.classList.add("node-children")
					object_new_parent_node.appendChild(ul)
				}

				object_new_parent_node.querySelector(".node-children").appendChild(object_node)

				if (!object_node.classList.contains("child-node"))
					object_node.classList.add("child-node")
			} else {

				if (object_node.classList.contains("child-node"))
					object_node.classList.remove("child-node")
				document.querySelector(".objects-tree__containing-list").appendChild(object_node)
			}
		}	
		show_message("Изменения сохранены")
	} else {
		show_message(ans["errors"]["__all__"][0])
	}
}

//Переслать данные об объекте на страницу с шаблоном
export function UpdateName(ans) {
	if (ans.res !== "ok")
		return
	window.opener.postMessage(JSON.stringify({
		name: ans.object.name,
		id: ans.object.id,
		optional: ans.object.optional,
		select: false
	}))
}

//Обновить option-ы в select-e формы создания/редактирования объектов
export function UpdateSelectorTree(ans) {

	if (ans.res !== "ok")
		return

	const parser = new DOMParser()
	const new_select_tag = parser.parseFromString(ans.select_tree, "text/html").querySelector("select")
	
	const field = document.querySelector(".edit-menu #connected-to")
	field.querySelector("select").remove()
	field.appendChild(new_select_tag)


}

// Заполнить форму данными объекта для его дальнейшего изменения
export function FillForm(ans) {
	document.querySelector("#ObjectModal .modal-title").innerHTML = "Редактирование объекта шаблона"

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
}

//Удалить объект из дерева
export function ObjectDeletionHandler(ans) {
	if (ans.res === "ok") {
		document.querySelector(`.node#id-${ans.object.id}`).remove()
		const parent = document.querySelector(`.node#id-${ans.object.connected_to}`)
		if (parent && document.querySelectorAll(`node#id-${ans.object.connected_to} > ul > li`).length === 0)
			parent.classList.add("leaf")
		show_message(`Объект ${ans.object.name} удaлен.`)
	}
	else {
		show_message(ans["error"])
	}
}