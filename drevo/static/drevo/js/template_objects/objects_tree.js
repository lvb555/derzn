// Код для страницы drevo/znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>
// не затрагивающий HTTP-запросы

const url = window.location.href.split("document-template")[0] + "document-template"
const message_block = document.querySelector(".log-container")
const expand_children = document.querySelectorAll(".node__expand-btn")
const collapse_children = document.querySelectorAll(".node__collapse-btn")
const objects_contaning_list = document.querySelector(".objects-tree__containing-list")

const turple_block = document.querySelector("#tuple") // поле выбора справочника

const subscription_block = document.querySelector("#subscription") // чекбокс "прописью"

const type = document.querySelector("#type_of select") // поле выбора типа содержимого
const types = { // допустимые типы содержимого
	"text": 0,
	"number": 1,
	"date": 2,
	"tuple": 3
}

export let deleting_object = null
export let action = null
export let editing_var = null

function update_state(e) {
	// обновить форму
	let is_turple = type.value == types["tuple"]
	subscription_block.style.display = type.value == types["text"] || is_turple ? "none" : "block"
	turple_block.style.display = type.value == types["tuple"] ? "block" : "none"
}

export function SelectObject(e) {
	const object = e.target.closest(".node")

	let availability
	if (object.classList.contains("local"))
		availability = 0
	else if (object.classList.contains("global"))
		availability = 1
	else if (object.classList.contains("general"))
		availability = 2

	window.opener.postMessage(
		JSON.stringify({
			name: object.querySelector("span").innerHTML,
			id: Number(object.id.split("-")[1]),
			select: true,
			optional: object.classList.contains("optional")
		}),
		window.opener.location.href)
	window.close()
}

export function ExpandCollapseNodeChildren(e) {
	e.target.closest(".img-block").classList.toggle("hidden")
	e.target.closest(".node").querySelector(".node-children").classList.toggle("hidden")

	let another_btn_class_name
	if (e.target.closest(".img-block").classList.contains("node__collapse-btn"))
		another_btn_class_name = ".node__expand-btn"
	else
		another_btn_class_name = ".node__collapse-btn"
	console.log(another_btn_class_name)
	e.target.closest(".node").querySelector(another_btn_class_name).classList.toggle("hidden")
}

export function SelecObjectToDelete(e) {
	console.log(e.target.closest(".node"))
	deleting_object = Number(e.target.closest(".node").id.split('-')[1])
}

document.querySelector(".edit-menu #type_of select").addEventListener("change", update_state)

document.querySelectorAll(".node:not(.group) > .node-label .node-label__name").forEach((i) => {
	i.addEventListener("dblclick", SelectObject)
})

expand_children.forEach((i) => {
	i.addEventListener('click', ExpandCollapseNodeChildren)
})

collapse_children.forEach((i) => {
	i.addEventListener('click', ExpandCollapseNodeChildren)
})

document.querySelector(".tree-actions button:first-child").addEventListener("click", update_state)

document.querySelectorAll(".node-actions .delete").forEach((btn) => {
	btn.addEventListener("click", SelecObjectToDelete)
})

document.querySelectorAll(".node-actions .edit").forEach(edit_btn => edit_btn.addEventListener("click", (e) => {
    action = "edit"
    editing_var = e.target.closest(".node").id.split("-")[1]
}))
document.querySelector(".tree-actions .btn:first-child").addEventListener("click", (e) => {
    action = "create"
    editing_var = null

	document.querySelectorAll('.edit-menu input[type="text"], .edit-menu select, .edit-menu textarea').forEach((elem) => {
		elem.value = ""
	})

	document.querySelectorAll('.edit-menu input[type="checkbox"]').forEach((elem) => {
		elem.checked = false
	})

	document.querySelectorAll('.edit-menu input[type="number"]').forEach((elem) => {
		elem.value = 100
	})
})
document.querySelector(".tree-actions .btn:last-child").addEventListener("click", (e) => {
	action="create"
	editing_var = null

	document.querySelector("#GroupModal .field input").value = ""
	document.querySelector("#GroupModal .field select").value = ""
})