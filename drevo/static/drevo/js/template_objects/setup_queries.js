export const csrftoken = getCookie("csrftoken")

export function TurpleEditID() {
	// собрать тело для запроса данных редактируемого справочника
	const body = new FormData()
	body.append("id", document.querySelector(".field#turple select").value)
	return body
}

export function ObjectProcessingBody (action, editing_var) {
	// собрать тело для запроса создания/редактирования объекта

	const body = new FormData()
	const edit_menu = document.querySelector(".edit-menu") // меню создания-редактирования переменной
	document.querySelectorAll(".edit-menu > .field input").forEach((i) => {

		console.log(i)

		if (i.type !== "checkbox" && i.type !== "radio"){
			body.append(i.name, i.value)
		} else if(i.type === "checkbox") {
			body.append(i.name, i.checked)
		} else if(i.checked) {
			body.append(i.name, i.value)
		}
	})

	edit_menu.querySelectorAll(".edit-menu > .field select").forEach((i) => {
		body.append(i.name, i.value)
	})

	edit_menu.querySelectorAll(".edit-menu > .field textarea").forEach((i) => {
		body.append(i.name, i.innerHTML)
	})

	body.append("action", action)
	body.append("knowledge", document.querySelector("#id_knowledge").value)

	if (editing_var !== null) {
		body.append("pk", editing_var)	
	}

	return body
}

function getCookie(name) {
	//получить нужный параметр из куки
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}