import {store} from './store.js'

export default {
  computed: {
    classObject() {
        return {disabled: store.selected.elementType!='d'}
    }
  },
  methods:{
   onEdit (){
       this.$root.tryTextEdit()
        },
   onCreate() { this.$root.createKnowledge() },
   onSelect() {this.$root.selectKnowledge() },
   onClear() {
        const [rowId, colId ] = store.selected.elementId
        store.tableData.clearCell(rowId, colId)
   },
   onState(val) {
        val = val - 1
        if (store.userLevel<val) return


        const [rowId, colId ] = store.selected.elementId
        let cell = store.tableData.getCell(rowId, colId, true)
        console.log(cell)
        // только свой уровень и ниже можем изменять
        if (cell.state > store.userLevel) return
            cell.state = val
    },
  },
  template: `
        <div class="card">
        <div class="card-header text-center">Наполнение ячеек</div>
        <div class="btn-group" role="group">
            <button @click="onEdit" id="btn_data_edit" title="Редактировать текст" type="button" class="btn btn-primary" :class="classObject">✐</button>
            <button @click="onCreate" id="btn_data_add" title="Добавить знание" type="button" class="btn btn-primary" :class="classObject">+</button>
            <button @click="onSelect" id="btn_data_select" title="Выбрать знание" type="button" class="btn btn-primary" :class="classObject">🗀</button>
            <button @click="onClear" id="btn_data_clear" title="Очистить ячейку" type="button" class="btn btn-primary" :class="classObject">🗑</button>
        </div>
        </div>`
}