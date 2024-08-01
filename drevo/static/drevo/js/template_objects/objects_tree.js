// Код для страницы drevo/znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>
// не затрагивающий HTTP-запросы

const expand_children = document.querySelectorAll(".node__expand-btn")
const collapse_children = document.querySelectorAll(".node__collapse-btn")

const turple_block = document.querySelector("#tuple") // поле выбора справочника

const subscription_block = document.querySelector("#subscription") // чекбокс "прописью"

const deleteModal = new bootstrap.Modal(document.getElementById('DeleteObjectModal'))
export const groupModal = new bootstrap.Modal(document.getElementById('GroupModal'))
export const objectModal = new bootstrap.Modal(document.getElementById('ObjectModal'))

const type = document.querySelector("#type_of select") // поле выбора типа содержимого
const types = { // допустимые типы содержимого
	"text": 0,
	"number": 1,
	"date": 2,
	"tuple": 3,
	"complex": 4
}

export let deleting_object = null
export let action = null
export let editing_var = null

function update_state(e) {
	// обновить форму
	let is_turple = type.value == types["tuple"]
	subscription_block.style.display = type.value == types["number"] || type.value == types["date"] ? "block" : "none"
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
	e.target.closest(".node").querySelector(another_btn_class_name).classList.toggle("hidden")
}

export function SelectObjectToDelete(e) {
	deleting_object = Number(e.target.closest(".node").id.split('-')[1])
}

export function SelectObjectToUpdate(e) {
	action = "edit"
    editing_var = e.target.closest(".node").id.split("-")[1]
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
	btn.addEventListener("click", SelectObjectToDelete)
})

document.querySelectorAll(".node-actions .edit").forEach(edit_btn => {
	edit_btn.addEventListener("click", SelectObjectToUpdate)
})
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