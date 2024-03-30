export const csrftoken = getCookie("csrftoken")

export function TurpleEditID() {
	// собрать тело для запроса данных редактируемого справочника
	const body = new FormData()
	body.append("id", document.querySelector(".field#turple select").value)
	return body
}

// export function TurpleProcessingBody(editing_turple) {
// 	// собрать тело для запроса создания/изменения справочника

// 	const form = document.querySelector(".turple-form")
// 	const body = new FormData()

// 	if (editing_turple !== null) {
// 		body.append("id", editing_turple)
// 	}
// 	body.append("name", form.querySelector("#id_name").value)
// 	body.append("weight", form.querySelector("#id_weight").value)
// 	body.append("knowledge", document.querySelector("#document_pk").value)

// 	document.querySelectorAll(".turple-menu__element").forEach((i) => {
// 		i.querySelectorAll("input").forEach((j) => {
// 			body.append(j.name, j.value)
// 		})
// 	})

// 	return body
// }

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
	body.append("knowledge", document.querySelector("#document_pk").value)

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