import {store} from './store.js'
export default {
    props: ['rowId','colId'],

    data(){
        return {
        store,
        timer: 0,
         }
    },
   mounted(){
    //console.log('i mounted')
   },
   computed: {
    classObject() {
        let cell = store.tableData.getCell(this.rowId,this.colId)
        let state = cell.state != undefined ? cell.state : -1
        return {
                selected: store.selected.isSelected('d', [this.rowId,this.colId]),
                is_text: !cell.id,
                'state-def': state == -1,
                'state-0': state === 0,  // обычное состояние
                'state-1': state === 1,  // проверено
                'state-2': state === 2,  // опублковано
            }
    }
  },
    methods: {
        onClick() {
            store.selected.select_element('d', [this.rowId,this.colId]);
            let now = new Date()
            let period = now - this.timer/1
            if (period <220) {
                //dblclick
                this.onEdit()
            }
            else this.timer = now
       },
       onEdit() {
        this.$root.tryTextEdit()
       },
    },
template: `
<td :class="classObject"
    @click="onClick"
    :key="{rowId, colId}">
    <div class="data_cell text-start p-1">
    <span>{{ store.tableData.getCellText(rowId, colId) }}</span>
  </div>
</td>`
}
