import {csrftoken} from "./setup_queries.js"

const zn_pk = document.querySelector(".template #document_pk").value
const pk = document.querySelector(".template #id_pk").value

function SaveTemplateBody() {
	const body = new FormData()
	body.append("content", CKEDITOR.instances.id_content.getData())
	body.append("zn_pk", zn_pk)
	body.append("pk", pk)

	return body
}

const url = window.location.href.split("document-template")[0] + "document-template/save-text-template"
const save_btn = document.querySelector(".template-btn.save")

document.addEventListener("DOMContentLoaded", (e) => {
	save_btn.addEventListener("click", (e) => {

		fetch(url, {"method":"post", "headers":{"X-CSRFToken":csrftoken}, "body": SaveTemplateBody()})
		.then(res => res.json())
		.then((ans) => {
			if (ans["res"] === "ok"){
				console.log("template saved")
			} else if (ans["res"] === "err"){
				console.log(ans["errors"])
			}
		})
	})
})