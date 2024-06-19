const url_to_select_page = window.location.href.slice(0, window.location.href.lastIndexOf("/", window.location.href.lastIndexOf("/") - 1))
const focused_object = document.querySelector(".object-card")
const focused_object_header = document.querySelector(".object-card__header")
const focused_object_block = document.querySelector(".template__selected-object")
const delete_btn = document.querySelector(".object-card__btn.delete")
const paste_btn = document.querySelector(".template__template-actions .paste")
const edit_btn = document.querySelector(".object-card__btn.edit")
let selected_object

document.querySelector(".template__template-actions .template-btn.select-obj").addEventListener("click", (e) => {
	window.open(url_to_select_page + "/object-select")	
})

window.addEventListener("message", (e) => {
	if (e.origin === window.origin) {
		selected_object = JSON.parse(e.data)
		focused_object_header.innerHTML = selected_object["name"]
		focused_object.id = selected_object["id"]
		focused_object_block.id = selected_object["id"]

		if (selected_object.availability < 2){

			if (delete_btn.classList.contains("hidden"))
				delete_btn.classList.remove("hidden")

			if (edit_btn.classList.contains("hidden"))
				edit_btn.classList.remove("hidden")
		} else {
			if (!delete_btn.classList.contains("hidden"))
				delete_btn.classList.add("hidden")

			if (!edit_btn.classList.contains("hidden"))
				edit_btn.classList.add("hidden")
		}
	}
})

document.addEventListener("DOMContentLoaded", (e) => {
	CKEDITOR.config.allowedContent = true
	const editor = CKEDITOR.instances.id_content

	editor.on("insertElement", (e) => {
		e.data["$"].addEventListener("keypress", (e) => {
			e.target.remove()
		})
	})
})


paste_btn.addEventListener("click", (e) => {
	if (document.readyState == 'complete') {
		let element
		element = CKEDITOR.dom.element.createFromHtml(`<span class="template-object" id="${selected_object.id}" contenteditable="false">&lt;${selected_object.name}&gt;</span>`)
		let space = CKEDITOR.dom.element.createFromHtml("<span>&nbsp;</span>")
		CKEDITOR.instances.id_content.insertElement(element)
		CKEDITOR.instances.id_content.insertElement(space)
	}
})
