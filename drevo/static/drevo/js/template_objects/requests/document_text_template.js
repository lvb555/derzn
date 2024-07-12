import {SaveTemplateBody} from "../setup_queries.js"
import {SaveTemplateHandler} from "../response_handlers/document_text_template.js"
import {url, csrftoken} from "./requirements.js"

// В этом файле обработчики событий, отправляющие запросы на бекенд со страницы
// drevo/znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>

const save_btn = document.querySelector(".template-btn.save")

// сохранить шаблон текста
document.addEventListener("DOMContentLoaded", (e) => {
	save_btn.addEventListener("click", (e) => {
		fetch(url + "/save-text-template", {"method":"post", "headers":{"X-CSRFToken":csrftoken}, "body": SaveTemplateBody()})
		.then(res => res.json())
		.then(ans => SaveTemplateHandler(ans))
	})
})