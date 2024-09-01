import {show_message, FindNextElement} from "./requirements.js"
import {
	SelectObject,
	ExpandCollapseNodeChildren,
	objectModal,
	groupModal,
	SetGroupLeafsAttentions,
	attentionButton,
	group_leafs_attentions
} from "../objects_tree.js"
import {ObjectInfoRequest} from "../requests/objects_tree.js"
import {SelectObjectToDelete} from "../objects_tree.js"
import {SelectObjectToUpdate} from "../objects_tree.js"


// В этом файле хранятся функции, меняющие DOM дерево в зависимости от ответа бекенда на запросы.
// со страницы drevo/znanie/<id>/document-template/object-select


// Добавляет новою вершину(лист) в дерево объектов. Вершина соответсвует новому объекту.
export function CreateNewObject(ans) {
	const object_template = document.querySelector(".node.clone")

	if (ans.res == "ok") {
		const object = object_template.cloneNode(true)
		let parent

		if (ans.object.connected_to) {
			parent = document.querySelector(`.node#id-${ans.object.connected_to}`)
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

		if (ans.object.is_main) {
			object.classList.add("group")
		} else {
			object.querySelector(".node-label__name").addEventListener("dblclick", SelectObject)
		}

		if (ans.object.optional) {
			object.classList.add("optional")
		}
			
		object.classList.add("leaf")
		object.classList.remove("clone")

		object.setAttribute("data-weight", ans.object.weight)
		object.setAttribute("id", `id-${ans.object.id}`)

		object.querySelector('.node-label__name span').innerHTML = (ans["object"].name)
		object.querySelector(".node__expand-btn").addEventListener("click", ExpandCollapseNodeChildren)
		object.querySelector(".node__collapse-btn").addEventListener("click", ExpandCollapseNodeChildren)
		object.querySelector(".node-actions .edit").addEventListener("click", ObjectInfoRequest)
		object.querySelector(".node-actions .edit").addEventListener("click", SelectObjectToUpdate)
		object.querySelector(".node-actions .delete").addEventListener("click", SelectObjectToDelete)
		
		const elem_to_insert_before = FindNextElement(Array.from(parent.children), ans.object.weight)
		if (elem_to_insert_before)
			parent.insertBefore(object, elem_to_insert_before)
		else
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

		object_node.setAttribute("data-weight", ans.object.weight)
		//Если сменился родитель объекта 
		const object_parent_node = object_node.parentElement.closest(".node")
		if ((object_parent_node !== null ^ ans.object.connected_to !== null) || object_parent_node && (object_parent_node.id !== `id-${ans.object.connected_to}`)) {
			object_node.remove()
			if (object_parent_node && object_parent_node.querySelectorAll(".node").length == 0)
				object_parent_node.classList.add("leaf")
			//Если объект не корневой
			if (ans.object.connected_to !== null) {
				let object_new_parent_node = document.querySelector(`.node#id-${ans.object.connected_to}`)
				object_new_parent_node.classList.remove("leaf")
				
				if (!object_new_parent_node.querySelector(".node-children")) {
					const ul = document.createElement("ul")
					ul.classList.add("node-children")
					object_new_parent_node.appendChild(ul)
				}

				// вставить в список детей родителя соотвествии с весом объекта
				const elem_to_insert_before = FindNextElement(Array.from(object_new_parent_node.querySelector(".node-children").children), ans.object.weight)
				if (elem_to_insert_before)
					object_new_parent_node.querySelector(".node-children").insertBefore(object_node, elem_to_insert_before)
				else
					object_new_parent_node.querySelector(".node-children").appendChild(object_node)

				if (!object_node.classList.contains("child-node"))
					object_node.classList.add("child-node")
			} else {

				if (object_node.classList.contains("child-node"))
					object_node.classList.remove("child-node")
				
				// вставить в список корневых элементов в соотвествии с весом объекта
				const elem_to_insert_before = FindNextElement(
												Array.from(document.querySelector(".objects-tree__containing-list").children),
												ans.object.weight
											)
				if (elem_to_insert_before)
					document.querySelector(".objects-tree__containing-list").insertBefore(object_node, elem_to_insert_before)
				else
					document.querySelector(".objects-tree__containing-list").appendChild(object_node)
			}
		} else {
			let object_cur_parent
			if (!object_parent_node)
				object_cur_parent = document.querySelector(".objects-tree__containing-list")
			else
				object_cur_parent = object_parent_node.querySelector(".node-children")
			
			
			// закончить работу, если новый вес не нарушает порядок в массиве детей
			if ((object_node.previousSibling.dataset ?? ans.object).weight <= ans.object.weight && ans.object.weight <= (object_node.nextSibling.dataset ?? ans.object).weight) {
				show_message("Изменения сохранены")
				return
			}

			// вставить в список детей родителя в соотвествии с весом объекта
			object_node.remove()
			const elem_to_insert_before = FindNextElement(Array.from(object_cur_parent.children), ans.object.weight)
			if (elem_to_insert_before)
				object_cur_parent.insertBefore(object_node, elem_to_insert_before)
			else
				object_cur_parent.appendChild(object_node)
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

	if (ans.res !== "ok") {
		return
	}
	let form
	if (ans.object.is_main){
		document.querySelector("#GroupModal .modal-title").innerHTML = "Редактирование объекта шаблона"
		form = document.querySelector("#GroupModal .modal-body")
		groupModal.show()
	} else {
		form = document.querySelector(".edit-menu")	
		document.querySelector("#ObjectModal .modal-title").innerHTML = "Редактирование объекта шаблона"
		objectModal.show()
		form.querySelector("textarea").value = ans.object.fill_title
	}

	form.querySelectorAll(".field input, .field select").forEach((i) => {
		if (i.type == "checkbox") {
			i.checked = ans.object[i.name]
		} else if (i.type == "radio") {
			i.checked = i.value == ans.object[i.name]
		} else {
			i.value = ans.object[i.name] !== null ? ans.object[i.name] : ""
		}
	})
}

//Удалить объект из дерева
export function ObjectDeletionHandler(ans) {
	if (ans.res === "ok") {
		document.querySelector(`.node#id-${ans.object.id}`).remove()
		const parent = document.querySelector(`.node#id-${ans.object.connected_to}`)
		if (parent && document.querySelectorAll(`.node#id-${ans.object.connected_to} > ul > li`).length === 0)
			parent.classList.add("leaf")
		show_message(`Объект ${ans.object.name} удaлен.`)
	}
	else {
		show_message(ans["error"])
	}
}

// Сохранить все ошибки дерева объектов
export function SaveAttentions(ans) {
	SetGroupLeafsAttentions(ans.group_leafs)
	attentionButton.style.display = group_leafs_attentions.length === 0 ? "none" : "inline-block"
}