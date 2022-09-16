class Tags {

    config = {
        tagContainerSelector: '.tags_set',
        tagsTotalFormsSelector: '#id_tags-TOTAL_FORMS',
        tagSwitcherSelector: '.tag_swither',
        tagPlusSelector: '.add-input',
        tagMinusSelector: '.delete-input',
        tagTemplateSelector: '.tag_template',
        tagFieldSelector: '.tag_field',
        templateId: 'id_tags-__prefix__-tag',
        tagKeyInStorage: 'tag-'

    }

    constructor() {
        const tagSet = document.querySelector(this.config.tagContainerSelector);

        this.tagsTotalForms = document.querySelector(this.config.tagsTotalFormsSelector);

        this.plusMinusChecker();

        tagSet.addEventListener('click',
            (event) => this.clickHandler(event));
    }

    getClassNameFromSelector(selector) {
        if (selector.startsWith('.')) {
            return selector.slice(1,)
        } else {
            throw new Error("Селектор не для класса");
        }
    }

    clickHandler(event) {
        // Определяем по чему был клик по плюсу или минусу
        const target = event.target.closest(this.config.tagSwitcherSelector);
        if (!target) return;

        const plusClass = this.getClassNameFromSelector(this.config.tagPlusSelector);
        const minusClass = this.getClassNameFromSelector(this.config.tagMinusSelector);

        if (target.classList.contains(plusClass)) {
            this.addInput(target);
        } else if (target.classList.contains(minusClass)) {
            this.deleteInput(target);
        }
    }

    plusMinusChecker() {
        this.showOnlyLastPlus();
        this.hideMinusIfOnlyOneElement();
    }

    hidePluses() {
        const pluses = document.querySelectorAll(this.config.tagPlusSelector);
        for (let plus of pluses) {
            plus.style.visibility = 'hidden';
        }
    }

    showOnlyLastPlus() {
        this.hidePluses();
        const pluses = document.querySelectorAll(`${this.config.tagFieldSelector} ${this.config.tagPlusSelector}`);
        pluses[pluses.length - 1].style.visibility = 'visible';
    }

    showMinuses() {
        const minuses = document.querySelectorAll(`${this.config.tagFieldSelector} ${this.config.tagMinusSelector}`);
        for (let minus of minuses) {
            minus.style.visibility = 'visible';
        }
    }

    hideMinusIfOnlyOneElement() {
        const minuses = document.querySelectorAll(`${this.config.tagFieldSelector} ${this.config.tagMinusSelector}`);
        if (minuses.length === 1) {
            minuses[0].style.visibility = 'hidden';
        } else {
            this.showMinuses();
        }
    }

    incrementTotalForms() {
        this.tagsTotalForms.value = +this.tagsTotalForms.value + 1;
    }

    decrementTotalForms() {
        this.tagsTotalForms.value = +this.tagsTotalForms.value - 1;
    }

    getNextFormNum() {
        return +this.tagsTotalForms.value;
    }

    getLastFormNum() {
        return +this.tagsTotalForms.value - 1;
    }

    renameAllEntries() {
        let outputTags = [];
        let inputTags = document.querySelectorAll(this.config.tagFieldSelector);
        const tagSet = document.querySelector(this.config.tagContainerSelector);

        let values = [];

        for (let i = 0; i <= this.getLastFormNum(); i++) {
            let value = inputTags[i].querySelector('input').value;
            let currentTag = this.getNewTagInput(i)

            inputTags[i].remove();
            outputTags.push(currentTag);
            values.push(value);
        }


        // Теперь добавляем outputTags в контейнер
        for (let i in outputTags) {
            let inputTag = outputTags[i].querySelector('input');
            inputTag.value = values[i];
            tagSet.append(outputTags[i]);
        }
    }

    getNewTagInput(num) {
        const template = this.getTemplateTag();

        const tagTemplateClass = this.getClassNameFromSelector(this.config.tagTemplateSelector);
        const tagFieldClass = this.getClassNameFromSelector(this.config.tagFieldSelector);

        let newTag = template.cloneNode(true);
        newTag.hidden = false;

        newTag.classList.remove(tagTemplateClass);
        newTag.classList.add(tagFieldClass);
        newTag.innerHTML = newTag.innerHTML.replaceAll('__prefix__', num);

        return newTag;
    }

    getFirstFreeInputTag() {
        let inputTags = document.querySelectorAll(this.config.tagFieldSelector);

        for (let i = 0; i <= this.getLastFormNum(); i++) {
            let inputTag = inputTags[i].querySelector('input');
            let value = inputTag.value;
            if (!value) {
                return inputTag
            }
        }
        return null;
    }

    getTemplateTag() {
        const tagTemplate = document.querySelector(this.config.tagTemplateSelector);
        return tagTemplate
    }

    addInput() {
        // Находим контейнер в который будем добавлять теги и находим шаблон тега
        const tagSet = document.querySelector(this.config.tagContainerSelector);

        let newTag = this.getNewTagInput(this.getNextFormNum());

        tagSet.append(newTag);
        this.incrementTotalForms();
        this.plusMinusChecker();
    }

    deleteInput(minus) {
        // Если остался только один элемент, то минус необходимо скрыть

        // Находим текущий элемент и удаляем его
        const currentTag = minus.closest(this.config.tagFieldSelector);

        currentTag.remove();

        // const minusClass = this.getClassNameFromSelector(this.config.tagMinusSelector);
        this.decrementTotalForms();

        this.renameAllEntries();

        this.plusMinusChecker();
    }

    syncTagInStorage() {
        // Сначало получим все значение выбранных тегов
        let inputTags = document.querySelectorAll(this.config.tagFieldSelector);
        let values = []
        for (let tag of inputTags) {
            let value = tag.querySelector('input').value;
            values.push(value);
        }

        let keys = Object.keys(localStorage);

        for (let key of keys) {
            if (key.startsWith(this.config.tagKeyInStorage)) {
                localStorage.removeItem(key);
            }
        }

        for (let num in values) {
            localStorage.setItem(this.config.tagKeyInStorage + num, values[num]);
        }

        localStorage.setItem('tags-TOTAL_FORMS', values.length);
    }

    restoreTagSet() {
        let values = [];

        let keys = Object.keys(localStorage);

        for (let key of keys) {
            if (key.startsWith(this.config.tagKeyInStorage)) {
                let value = localStorage.getItem(key);
                if (value) {
                    values.push(localStorage.getItem(key));
                }
            }
        }

        for (let value of values) {
            const firstFreeInputTag = this.getFirstFreeInputTag();

            firstFreeInputTag.value = value;
            this.addInput(false);
        }
    }

    cleanTagStorage() {
        localStorage.clear();
    }
}

