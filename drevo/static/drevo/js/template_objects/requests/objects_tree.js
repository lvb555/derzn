import {ObjectProcessingBody, GroupProcessingBody} from "../setup_queries.js"
import {
	CreateNewObjec,
	FillForm,
	UpdateTree,
	UpdateName,
	UpdateSelectorTree,
	ObjectDeletionHandler,
	SaveAttentions
} from "../response_handlers/objects_tree.js"
import {url, csrftoken} from "./requirements.js"
import {action, editing_var, deleting_object} from "../objects_tree.js"

// В этом файле обработчики событий, отправляющие запросы на бекенд со страницы
// drevo/znanie/<id>/document-template/object-select

// Запрос информации об объекте, чтобы отобразить ее в форме(если пользователь изменяет объект)
export function ObjectInfoRequest(e) {
	const editing_var = e.target.closest(".node").id.split("-")[1]
	return fetch(url + `/document_object_processing?id=${editing_var}`, {"method": "get", "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => { return response.json() })
	.then((ans) => {
		FillForm(ans)
		const promise = new Promise((resolve, reject) => resolve("ok"))
		return promise
	})
}

// Запрос на создание нового объекта или изменение существующего
function ObjectProcessingRequest(e) {
	let body
	if (e.target.closest("#ObjectModal"))
		body = ObjectProcessingBody(action, editing_var)
	else
		body = GroupProcessingBody(action, editing_var)
	return  fetch(url + "/document_object_processing", {"method": "post", "body": body, "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => response.json())
	.then((ans) => {
		if(action === "create")
			CreateNewObjec(ans)
		else {
			UpdateTree(ans)
			UpdateName(ans)
		}
		UpdateSelectorTree(ans)
		const promise = new Promise((resolve, reject) => {resolve('ok')})
		return promise
	})
}

// удалить объект
function ObjectDeletionRequest(e) {
	return fetch(url + `/document_object_deletion?id=${deleting_object}`, {"method": "delete", "headers": {"X-CSRFToken": csrftoken}})
	.then((response) => response.json())
	.then((ans) => {
		ObjectDeletionHandler(ans)
		UpdateSelectorTree(ans)
		const promise = new Promise((resolve, reject) => {resolve('ok')})
		return promise
	})
}

// Проверка наличия ошибок в дереве
function ObjectTreeCorrectnessCheck(e) {
	fetch(url + "/object_tree_correctness", {"method": "get", "headers": {"X-CSRFToken": csrftoken}})
	.then(response => response.json())
	.then(ans => {
		SaveAttentions(ans)
	})
}

ObjectTreeCorrectnessCheck(null)

// привязка функций к событиям
document.querySelectorAll(".edit-menu__save-btn").forEach((i) => i.addEventListener('click', (e) => {
	ObjectProcessingRequest(e)
	.then(() => {
		ObjectTreeCorrectnessCheck(e)
	})

}))

document.querySelectorAll(".node-actions .edit").forEach(edit_btn => edit_btn.addEventListener("click", (e) => {
	ObjectInfoRequest(e)
	.then(() => {
		ObjectTreeCorrectnessCheck(e)
	})
}))

document.querySelector(".object-delete-menu .btn:first-child").addEventListener('click', (e) => {
	ObjectDeletionRequest(e)
	.then(() => {ObjectTreeCorrectnessCheck(e)})
})
