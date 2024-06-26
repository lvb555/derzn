import {SaveTemplateHandler} from "./response_handlers/document_text_template.js"
import {SaveTemplateBody} from "./setup_queries.js"
import {csrftoken, url} from "./requests/requirements.js"

// Код для страницы drevo/znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>
// не затрагивающий HTTP-запросы

const url_to_select_page = window.location.href.slice(0, window.location.href.lastIndexOf("/", window.location.href.lastIndexOf("/") - 1))

const focused_object = document.querySelector(".object-card")
const focused_object_header = document.querySelector(".object-card__header")
const focused_object_block = document.querySelector(".template__selected-object")

const delete_btn = document.querySelector(".object-card__btn.delete")
const paste_btn = document.querySelector(".template__template-actions .paste")
const edit_btn = document.querySelector(".object-card__btn.edit")

let selected_object = null

document.querySelector(".template__template-actions .template-btn.select-obj").addEventListener("click", (e) => {
	window.open(url_to_select_page + "/object-select")	
})

window.addEventListener("message", (e) => {
	if (e.origin === window.origin) {
		const data = JSON.parse(e.data)
		if (data.select) {
			focused_object_header.innerHTML = data.name
			focused_object.id = data.id
			focused_object_block.id = data.id
			if (data.optional && !focused_object_block.classList.contains("optional"))
				focused_object_block.classList.add("optional")
			else if (!data.optional && focused_object_block.classList.contains("optional"))
				focused_object_block.classList.remove("optional")

			selected_object = {name: data.name, id: data.id, optional: data.optional}
		} else if (data.id == focused_object.id) {
			focused_object_header.innerHTML = data.name
		}

		if (document.readyState === 'complete') {
			const editor = CKEDITOR.instances.id_content
			const objects_in_text = editor.document.$.body.querySelectorAll(`.template-object#id-${data.id}`)
			objects_in_text.forEach((object) => {
				object.innerHTML = `&lt;${data.name}&gt;`
			})

			fetch(url + "/save-text-template", {"method":"post", "headers":{"X-CSRFToken":csrftoken}, "body": SaveTemplateBody()})
			.then(res => res.json())
			.then(ans => SaveTemplateHandler(ans))
		}
	}
})

document.addEventListener("DOMContentLoaded", (e) => {
	CKEDITOR.config.allowedContent = true
	const editor = CKEDITOR.instances.id_content

	editor.on("insertElement", (e) => {
		e.data.$.addEventListener("keypress", (e) => {
			e.target.remove()
		})
	})
})


paste_btn.addEventListener("click", (e) => {
	if (document.readyState === 'complete') {

		console.log(selected_object)

		if (selected_object.optional) {
			let object_html_code = `<span contenteditable="false" id="${selected_object.id}">{<span contenteditable="true">&nbsp;</span><span>[${selected_object.name}]</span>}</span>`
  			console.log(object_html_code)
  			CKEDITOR.instances.id_content.insertHtml(object_html_code)
		} else {
			let element = CKEDITOR.dom.element.createFromHtml(`<span class="template-object" id="id-${selected_object.id}" contenteditable="false">&lt;${selected_object.name}&gt;</span>`)
			let space = CKEDITOR.dom.element.createFromHtml("<span>&nbsp;</span>")
			CKEDITOR.instances.id_content.insertElement(element)
			CKEDITOR.instances.id_content.insertElement(space)
		}
	}
})