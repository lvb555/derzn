document.querySelectorAll(".node-name").forEach((i) => {
	i.addEventListener("dblclick", (e) => {
		const p = e.target.closest(".node-name")
		const object_name = p.querySelector("span").innerHTML
		const id = Number(p.id.split("-")[1])
		let availability = -1
		if (p.classList.contains("local"))
			availability = 0
		else if (p.classList.contains("global"))
			availability = 1
		else if (p.classList.contains("general"))
			availability = 2

		window.opener.postMessage(
			JSON.stringify({
				"name": object_name,
				"id": id,
				"availability": availability
			}),
			window.opener.location.href)
		window.close()
	})
})