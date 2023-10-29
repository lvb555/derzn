function getAddButtons() {
	return document.querySelectorAll('.same_type_suggestions__add')
}

function getRemoveButtons() {
	return document.querySelectorAll('.field__remove')	
}

function getButtonType(btn) {
	return Number(btn.getAttribute('id').split('-')[1])
}

function getFiedlsBlock(type) {
	return document.querySelector(`#fields-of-type-${type}`)
}

function getCountOfFields(block) {
	return block.querySelectorAll('.field').length
}

function isFieldEmpty(field) {
	return field.querySelector('textarea').value.length === 0
}

function createNewField(event) {
	let type = getButtonType(event.target)
	let block = getFiedlsBlock(type)

	if (getCountOfFields(block) < 5 && !isFieldEmpty(block.querySelector('.field:last-child'))) {
		let textarea = document.createElement('textarea')
		textarea.name=`field-of-type-${type}`
		textarea.classList.add('form-control')
		textarea.classList.add('field__area')
		textarea.rows = 2
		textarea.setAttribute('maxlength', 255)
		textarea.placeholder = "Введите текст предложения"

		let rm_btn = document.createElement('button')
		rm_btn.innerHTML = '-'
		rm_btn.classList.add('field__remove')
		rm_btn.classList.add('btn')
		rm_btn.classList.add('btn-header')
		rm_btn.type = 'button'
		rm_btn.addEventListener('click', deleteLastField)

		let field = document.createElement('div')
		field.classList.add('field')
		field.append(textarea)
		field.append(rm_btn)

		block.append(field)

		event.target.style.top = `${100 - 100 / getCountOfFields(block)}%`
	}
}

function deleteLastField(event) {
	field_block = event.target.parentElement
	if (!isFieldEmpty(field_block) || getCountOfFields(field_block.parentElement) === 1){
		return
	}
	let block = null

	if (field_block !== null) {
		block = field_block.parentElement.parentElement
		field_block.remove()
	}

	if (block !== null) {
		block.querySelector('.same_type_suggestions__add').style.top = `${100 - 100 / getCountOfFields(block)}%`
	}

}

function setEventListeners(buttons, foo, event='click') {
	buttons.forEach((btn) => {
		btn.addEventListener(event, foo)
	})
}

setEventListeners(getAddButtons(), createNewField)
setEventListeners(getRemoveButtons(), deleteLastField)