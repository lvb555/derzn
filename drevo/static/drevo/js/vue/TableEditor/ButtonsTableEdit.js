import { store } from './store.js'

export default {
  data(){
        return {store, prevElement:''}
  },
  computed: {
    classObject() {
        return {
            disabled: (!store.userPermissions.changeTable || store.selected.elementType!='c' && store.selected.elementType!='r'),
            btn: true,  
            'btn-primary': true }
    },
    isRow() {
        let result = ''
        const defaultValue = true
        if (store.selected.elementType=='r') result='r'
        else if (store.selected.elementType=='c') result='c'
        else if (this.prevElement) result=this.prevElement

        if (result) {
            this.prevElement = result
            return result=='r' }
        return defaultValue
    }
  },
  template: `
        <div class="card">
        <div class="card-header text-center">Конструктор строк и столбцов</div>
        <div class="btn-group"  role="group">
            <template v-if="isRow">
                <button title="Добавить строку" @click="store.tableData.addRow('')" id="btn_row_add" type="button" :class="classObject">+</button>
                <button title="Удалить строку" @click="store.tableData.delColRow('r', store.selected.elementId)" id="btn_row_del" type="button" :class="classObject">-</button>
                <button title="Выше" @click="store.tableData.headerMove(store.selected.elementId,'r','-')" id="btn_row_up" type="button" :class="classObject">▲</button>
                <button title="Ниже" @click="store.tableData.headerMove(store.selected.elementId,'r','+')" id="btn_row_down" type="button" :class="classObject">▼</button>
            </template>
            <template v-if="!isRow">
                <button title="Добавить колонку" @click="store.tableData.addCol('')" id="btn_col_add" type="button" :class="classObject">+</button>
                <button title="Удалить колонку" @click="store.tableData.delColRow('c', store.selected.elementId)" id="btn_col_del" type="button" :class="classObject">-</button>
                <button title="Сместить колонку влево" @click="store.tableData.headerMove(store.selected.elementId,'c','-')" id="btn_col_left" type="button" :class="classObject">⯇</button>
                <button title="Сместить колонку вправо" @click="store.tableData.headerMove(store.selected.elementId,'c','+')" id="btn_col_right" type="button" :class="classObject">⯈</button>
            </template>
        </div>
        </div>`
}