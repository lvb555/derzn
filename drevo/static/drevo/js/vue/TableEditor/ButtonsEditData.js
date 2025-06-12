import {store} from './store.js'

export default {
  computed: {
//    classObject() {
//        return {disabled: store.selected.elementType!='d'}
//    },

  },
  methods:{
  stateButtonEnabled(level) {
        if (store.selected.elementType!='d') {return {disabled: true}}

        const [rowId, colId ] = store.selected.elementId
        let cell = store.tableData.getCell(rowId, colId)
        //если уровень ячейки выше или равен, но не этот пользователь автор статуса
        if ((cell.state > store.userLevel) ||
            (
            (cell.state == store.userLevel) &&
            (cell.state_user_id && (cell.state_user_id != store.user_id))
            )) {
                return {disabled: true}
            }
        return {disabled: !(store.userLevel>=(level-1))}


  },
  editButtonEnabled(button) {
     if (store.selected.elementType!='d') {return {disabled: true}}
     const [rowId, colId ] = store.selected.elementId
     const cell = store.tableData.getCell(rowId, colId)
     let flag = true
     switch (button) {
     case 'edit':
        flag = store.tableData.canChange(rowId, colId) && !cell.id
        break;

     case 'create':
     case 'select':
        flag = store.tableData.canFillEmpty(rowId, colId) && store.tableData.isCellFree()
        break;

     case 'clear':
        flag = store.tableData.canDelete(rowId, colId) && !store.tableData.isCellFree()
        break;

     }
        return {disabled: !flag}
  },
   onEdit (){
       this.$root.tryTextEdit()
  },
   onCreate() { this.$root.createKnowledge() },
   onSelect() {this.$root.selectKnowledge() },
   onClear() {this.$root.tryClear() },
   onState(val) {
        val = val - 1
        if (store.userLevel<val) return
        const [rowId, colId ] = store.selected.elementId
        let cell = store.tableData.getCell(rowId, colId)

        // только свой уровень и ниже можем изменять
        if (cell.state > store.userLevel) return
        // если статусы равны, то можно если это автор статуса
        if ((cell.state == store.userLevel) &&
            (cell.state_user_id && cell.state_user_id != store.user_id)) return

        // создаем ячейку если ее нет
        cell = store.tableData.getCell(rowId, colId, true)
        cell.state = val
        cell.state_user_id = store.user_id
        store.isChanged = true

    },
  },
  template: `
        <div class="card">
        <div class="card-header text-center">Наполнение ячеек</div>
        <div class="btn-group" role="group">
            <button @click="onEdit" id="btn_data_edit" title="Редактировать текст" type="button" class="btn btn-primary" :class="editButtonEnabled('edit')">✐</button>
            <button @click="onCreate" id="btn_data_add" title="Добавить знание" type="button" class="btn btn-primary" :class="editButtonEnabled('create')">+</button>
            <button @click="onSelect" id="btn_data_select" title="Выбрать знание" type="button" class="btn btn-primary" :class="editButtonEnabled('select')">🗀</button>
            <button @click="onClear" id="btn_data_clear" title="Очистить ячейку" type="button" class="btn btn-primary" :class="editButtonEnabled('clear')">🗑</button>
        </div>
        <div class="card-header text-center">Этап</div>
        <div class="btn-group" role="group">
            <button @click="onState(1)" id="btn_data_1" title="I" type="button" class="btn btn-primary" :class="stateButtonEnabled(1)">СОЗД</button>
            <button @click="onState(2)" id="btn_data_2" title="II" type="button" class="btn btn-primary" :class="stateButtonEnabled(2)">РЕД</button>
            <button @click="onState(3)" id="btn_data_3" title="III" type="button" class="btn btn-primary" :class="stateButtonEnabled(3)">ПУБЛ</button>
        </div>
        </div>`
}