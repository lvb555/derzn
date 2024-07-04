import {show_message} from "./requirements.js"

// В этом файле хранятся функции, меняющие DOM дерево в зависимости от ответа бекенда на запросы
// со страницы drevo/znanie/<int:doc_pk>/document-template/edit-text/<int:text_pk>

export function SaveTemplateHandler(ans) {
	if (ans["res"] == "ok") {
		show_message("Изменения сохранены")
	} else if (ans["res"] === "err") {
		show_message(ans["errors"]["__all__"][0])
	}
}