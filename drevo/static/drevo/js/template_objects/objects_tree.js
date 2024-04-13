import {ObjectProcessingBody, GroupProcessingBody, csrftoken} from "./setup_queries.js"

const url = window.location.href.split("document-template")[0] + "document-template"
const message_block = document.querySelector(".log-container")
const expand_children = document.querySelectorAll(".node__expand-btn")
const collapse_children = document.querySelectorAll(".node__collapse-btn")
const object_template = document.querySelector(".node.clone")
const objects_contaning_list = document.querySelector(".objects-tree__containing-list")

function select_obejct(e) {
	const p = e.target.closest(".node-name")
	const object_name = p.querySelector("span").innerHTML
	const id = Number(p.id.split("-")[1])
	let availability = -1
	if (p.classList.contains("local"))
		availability = 0
	else if (p.classList.contains("global"))
		availability = 1
	else if (p.classList.contains("general"))
		availability = 2

	window.opener.postMessage(
		JSON.stringify({
			"name": object_name,
			"id": id,
			"availability": availability
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

document.querySelector(".edit-menu__save-btn").addEventListener('click', (e) => {
	let body
	if (e.target.closest("#ObjectModal"))
		body = ObjectProcessingBody("create", null)
	else
		body = GroupProcessingBody()

	console.log(body)

	fetch(url + "/document_object_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		let message = document.createElement("p")
		message.classList.add("log-container__log")
		console.log(ans)
		if (ans["res"] == "ok") {
			message.innerHTML = "Объект создан"

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
				parent = objects_contaning_list
			}
			if (ans["object"].is_main) {
				object.classList.add("group")
			} else {
				object.querySelector(".node-name").addEventListener("dblclick", select_obejct)
			}
			object.classList.add("leaf")
			object.setAttribute("id", `id-${ans["object"].id}`)

			object.querySelector('.node-name span').innerHTML = (ans["object"].name)
			object.querySelector(".node__expand-btn").addEventListener("click", expand_collapse_node_children)
			object.querySelector(".node__collapse-btn").addEventListener("click", expand_collapse_node_children)
			object.classList.remove("clone")
			parent.appendChild(object)
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
					message.remove()
					message_block.style.display = "none"
				}, 510)
			}, 1500)
		}, 10)
	})
}))

expand_children.forEach((i) => {
	i.addEventListener('click', expand_collapse_node_children)
})

collapse_children.forEach((i) => {
	i.addEventListener('click', expand_collapse_node_children)
})