function getAddButtons() {
	return document.querySelectorAll('.same_type_suggestions__add')
}

function getRemoveButtons() {
	return document.querySelectorAll('.same_type_suggestions__remove')	
}

function getButtonType(btn) {
	return Number(btn.getAttribute('id').split('-')[1])
}

function getFiedlsBlock(type) {
	return document.querySelector(`#fields-of-type-${type}`)
}

function getCountOfFields(block) {
	return block.querySelectorAll('input').length
}

function createNewField(event) {
	let type = getButtonType(event.target)
	let block = getFiedlsBlock(type)

	if (getCountOfFields(block) < 5) {
		let input = document.createElement('input')
		input.type='text'
		input.name=`field-of-type-${type}`
		input.className = 'form-control'
		block.append(input)
	}
}

function deleteLastField(event) {
	let type = getButtonType(event.target)
	let block = getFiedlsBlock(type)
	if (getCountOfFields(block) > 1) {
		block.querySelector('input:last-child').remove()
	}
}

function setEventListeners(buttons, foo) {
	buttons.forEach((btn) => {
		btn.addEventListener('click', foo)
	})
}

setEventListeners(getAddButtons(), createNewField)
setEventListeners(getRemoveButtons(), deleteLastField)