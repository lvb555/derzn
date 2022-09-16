`using strict`
// Обрабока полей расширенного поиска
class ExtendedField {
    config = {
        buttonId: 'collapseExtendedSearchButton',
        extendedField: 'collapseExtendedSearch',
        needResetField: true,
    }

    constructor(userConfig) {
        Object.assign(this.config, userConfig);

        this.extendedButton = document.getElementById(this.config.buttonId);
        this.extendedArea = document.getElementById(this.config.extendedField);
        this.extendedButton.addEventListener('click', (event) => this.saveExtendedFlag(event));
    }

    saveExtendedFlag(event) {
        let searchField_iWantCollapse = Boolean(localStorage.getItem(this.config.extendedField));
        if (searchField_iWantCollapse) {
            localStorage.removeItem(this.config.extendedField);
            if (this.config.needResetField) {
                this.resetExtendedFields();
            }
        } else {
            localStorage.setItem(this.config.extendedField, 'true');
        }
    }

    restoreArea() {
        if (localStorage.getItem(this.config.extendedField) === 'true') {
            this.extendedArea.classList.add('show');
        }
    }

    resetExtendedFields() {
        let fields = this.extendedArea.querySelectorAll('.form-control');
        for (let field of fields) {
            field.value = '';
        }
    }

}




