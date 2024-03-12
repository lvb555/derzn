const url_to_select_page = window.location.href.slice(0, window.location.href.lastIndexOf("/", window.location.href.lastIndexOf("/") - 1))
const focused_object = document.querySelector(".object-card")
const focused_object_header = document.querySelector(".object-card__header")
const focused_object_block = document.querySelector(".template__selected-object")
const delete_btn = document.querySelector(".object-card__btn.delete")
const paste_btn = document.querySelector(".template__template-actions .paste")

document.querySelector(".template__template-actions .template-btn.select-obj").addEventListener("click", (e) => {
	window.open(url_to_select_page + "/object-select")	
})

window.addEventListener("message", (e) => {
	if (e.origin === window.origin) {
		let res = JSON.parse(e.data)
		focused_object_header.innerHTML = res["name"]
		focused_object.id = res["id"]
		focused_object_block.id = res["id"]

		console.log(res)
		if (res["availability"] == 0){
			if (delete_btn.classList.contains("hidden"))
				delete_btn.classList.remove("hidden")
		} else {
			if (!delete_btn.classList.contains("hidden")) {
				delete_btn.classList.add("hidden")
			}
		}
	}
})

document.addEventListener("DOMContentLoaded", (e) => {
	CKEDITOR.config.allowedContent = true
	CKEDITOR.instances.id_content.on("insertElement", (e) => {
		console.log(e.data["$"].innerHTML)
		e.data["$"].addEventListener("keypress", (e) => {
			e.target.remove()
		})
	})
})

paste_btn.addEventListener("click", (e) => {
	if (document.readyState == 'complete') {
		let element = CKEDITOR.dom.element.createFromHtml(`<span contenteditable="false"><${focused_object_header.innerHTML}></span>`)
		let space = CKEDITOR.dom.element.createFromHtml("<span>&nbsp;</span>")
		CKEDITOR.instances.id_content.insertElement(element)
		CKEDITOR.instances.id_content.insertElement(space)
	}
})
