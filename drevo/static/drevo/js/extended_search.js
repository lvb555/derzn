`using strict`
// Обрабока полей расширенного поиска
extendedSearch = {
    extendedSearchButton: document.getElementById('collapseExtendedSearchButton'),
    collapseImg: document.getElementById('extendedSearchButtonImg'),
    extendedSearchArea: document.getElementById('collapseExtendedSearch'),
    init() {
        this.extendedSearchButton.addEventListener('click', (event) => this.saveExtendedFlag(event));
    },
    // Перехватываем раскрытие расширенного поиска и сохраняем этот факт
    saveExtendedFlag(event) {
        let searchField_iWantCollapse = Boolean(localStorage.getItem('isSearchExtanded'));
        if (searchField_iWantCollapse) {
            localStorage.removeItem('isSearchExtanded');
            this.resetExtendedSearchFields();
        } else {
            localStorage.setItem('isSearchExtanded', 'true');
        }
    },
    // Восстанавливаем состояние полей поиска после перезагрузки страницы
    restoreConditionSearchArea() {
        if (localStorage.getItem('isSearchExtanded') === 'true') {
            this.extendedSearchArea.classList.add('show');
        }
    },
    // Сбрасываем значения полей если схлопываем расширенный поиск
    resetExtendedSearchFields() {
        let fields = this.extendedSearchArea.querySelectorAll('.form-control');
        for (let field of fields) {
            field.value = '';
        }
    },
}

extendedSearch.init();
extendedSearch.restoreConditionSearchArea();