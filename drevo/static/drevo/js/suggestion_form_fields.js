function getAddButtons() {
	return document.querySelectorAll('.same_type_suggestions__add')
}

function getRemoveButtons() {
	return document.querySelectorAll('.field__remove')	
}

function getSendButton() {
	return document.querySelector('.suggestion-form__btn button')
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
		textarea.addEventListener('keyup', changeButtonsMode)
		textarea.placeholder = "Введите текст предложения"

		let rm_btn = document.createElement('button')
		rm_btn.innerHTML = '-'
		rm_btn.classList.add('field__remove')
		rm_btn.classList.add('btn')
		rm_btn.classList.add('btn-header')
		rm_btn.type = 'button'
		rm_btn.addEventListener('click', deleteField)

		let field = document.createElement('div')
		field.classList.add('field')
		field.append(textarea)
		field.append(rm_btn)

		block.append(field)

		event.target.style.top = `${100 - 100 / getCountOfFields(block)}%`
		event.target.disabled = true
	}
}

function deleteField(event) {
	field_block = event.target.parentElement
	if (!isFieldEmpty(field_block) || getCountOfFields(field_block.parentElement) === 1){
		return
	}

	add_btn = field_block.parentElement.parentElement.querySelector('.same_type_suggestions__add')

	let block = null

	if (field_block !== null) {
		block = field_block.parentElement.parentElement
		field_block.remove()
	}

	block_fields = Array.from(getFiedlsBlock(getButtonType(add_btn)).querySelectorAll('.field'))
	add_btn.disabled = block_fields.some((elem) => {return isFieldEmpty(elem)})

	if (block !== null) {
		block.querySelector('.same_type_suggestions__add').style.top = `${100 - 100 / getCountOfFields(block)}%`
	}

	if (block.querySelectorAll('.field').length == 1){
		block.querySelector('.field__remove').disabled = true
	}
}

function changeButtonsMode(event) {
	let fields_list = Array.from(document.querySelectorAll('.field'))
	getSendButton().disabled = fields_list.every((elem) => {return isFieldEmpty(elem)})

	add_btn = event.target.parentElement.parentElement.parentElement.querySelector('.same_type_suggestions__add')
	fields_block = getFiedlsBlock(getButtonType(add_btn))
	rm_btn = event.target.parentElement.querySelector('.field__remove')

	fields_in_block = Array.from(fields_block.querySelectorAll('.field'))
	add_btn.disabled = fields_in_block.some((elem) => {return isFieldEmpty(elem)}) || fields_block.querySelectorAll('.field').length === 5
	rm_btn.disabled = event.target.value.length !== 0 || fields_block.querySelectorAll('.field').length === 1
}

function addEventListeners(elems, foo, event='click') {
	elems.forEach((elem) => {
		elem.addEventListener(event, foo)
	})
}

addEventListeners(getAddButtons(), createNewField)
addEventListeners(getRemoveButtons(), deleteField)

let all_fields_list = document.querySelectorAll('.field textarea')
addEventListeners(all_fields_list, changeButtonsMode, 'keyup')
