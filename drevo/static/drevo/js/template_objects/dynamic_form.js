let turple_block = document.querySelector("#tuple") // поле выбора справочника

let subscription_block = document.querySelector("#subscription") // чекбокс "прописью"

let type = document.querySelector("#type_of select") // поле выбора типа содержимого
let types = { // допустимые типы содержимого
	"text": 0,
	"number": 1,
	"date": 2,
	"tuple": 3
}


export function update_state(e) {
	// обновить форму
	let is_turple = type.value == types["tuple"]
	subscription_block.style.display = type.value == types["text"] || is_turple ? "none" : "block"
	turple_block.style.display = type.value == types["tuple"] ? "block" : "none"
}

document.querySelector("#structure input").addEventListener("change", update_state)

// изменили тип значения
document.querySelector("#type_of select").addEventListener("change", update_state)
