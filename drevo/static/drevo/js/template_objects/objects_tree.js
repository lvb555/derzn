
const url = window.location.href.split("document-template")[0] + "document-template"
const message_block = document.querySelector(".log-container")
const expand_children = document.querySelectorAll(".node__expand-btn")
const collapse_children = document.querySelectorAll(".node__collapse-btn")
const objects_contaning_list = document.querySelector(".objects-tree__containing-list")

function select_obejct(e) {
	const object = e.target.closest(".node")
	const object_name = object.querySelector("span").innerHTML
	const id = Number(object.id.split("-")[1])
	let availability = -1
	let optional = false
	if (object.classList.contains("local"))
		availability = 0
	else if (object.classList.contains("global"))
		availability = 1
	else if (object.classList.contains("general"))
		availability = 2

	if (object.classList.contains("optional"))
		optional = true


	window.opener.postMessage(
		JSON.stringify({
			"name": object_name,
			"id": id,
			"availability": availability,
			"optional": optional
		}),
		window.opener.location.href)
	window.close()
}

function expand_collapse_node_children(e) {
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

document.querySelectorAll(".node:not(.group) > .node-name").forEach((i) => {
	i.addEventListener("dblclick", select_obejct)
})


expand_children.forEach((i) => {
	i.addEventListener('click', expand_collapse_node_children)
})

collapse_children.forEach((i) => {
	i.addEventListener('click', expand_collapse_node_children)
})

document.querySelector(".tree-actions button:first-child").addEventListener("click", update_state)