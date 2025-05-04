const {reactive, ref} = Vue
import {store} from './store.js'
export default {
  setup() {
    const isDragable = ref(true)

    function getDataCell(index_row, index_col) { return store.tableData.getCellByIndex(index_row, index_col)}
    return {  isDragable, getDataCell, store }
  },
  methods: {
    startDrag(evt, itemPos, elType){
      evt.dataTransfer.dropEffect = 'move'
      evt.dataTransfer.effectAllowed = 'move'
      evt.dataTransfer.setData('itemPos', itemPos)
      evt.dataTransfer.setData('elType', elType)
      console.log('start')
    },
    onDrop(evt, newPos, elType){
        const itemPos = evt.dataTransfer.getData('itemPos')
        const drag_elType = evt.dataTransfer.getData('elType')
        //console.log(itemPos, newPos)
        if (drag_elType != elType)   return
        store.tableData.move(itemPos, newPos, elType)
        },
      //evt.preventDefault();

  },
  template: `
        <div  class="table-responsive">
        <table  border="1">
            <thead>
                <tr>
                  <th colspan="2" rowspan="2" @dblclick="$refs.group.editing=true">
                    <TextCell ref="group" v-model:caption="store.tableData.group"/>
                  </th>
                  <th :colspan="store.tableData.cols.length"><TextCell v-model:caption="store.tableData.group_col" /></th>

                </tr>
                <tr>
                    <th v-for="(col, index_col) of store.tableData.cols" scope="col"
                          :key="'c'+col.id"
                          :class="{ selected: store.selected.isSelected('c', col.id), newColRow: store.tableData.cols[index_col].isNew  }"
                          @click="store.selected.select_element('c', col.id)"
                          :draggable="isDragable"
                          @dragstart.shift.capture.exact="startDrag($event, index_col, 'c')"
                          @dragstart.exact.prevent
                          @drop="onDrop($event, index_col, 'c')"
                          @dragover.prevent
                          @dragenter.prevent> <TextCell :draggable="isDragable" v-model:caption="store.tableData.cols[index_col].name" /> </th>

                </tr>
            </thead>
            <tbody>
                <tr v-for="(row, index_row) in store.tableData.rows" :key="row.id" class="">
                    <th @dblclick="$refs.group_row[0].editing=true" v-if="!index_row" :rowspan="store.tableData.rows.length">
                        <TextCell ref="group_row" v-model:caption="store.tableData.group_row" />
                    </th>
                    <th scope="row"
                        :key="'r'+row.id"
                        :class="{ selected: store.selected.isSelected('r', row.id), newColRow: store.tableData.rows[index_row].isNew }"
                          :draggable="isDragable"
                          @click="store.selected.select_element('r', row.id)"
                          @dragstart.shift.capture.exact="startDrag($event, index_row, 'r')"
                          @dragstart.exact.prevent
                          @drop="onDrop($event, index_row, 'r')"
                          @dragover.prevent
                          @dragenter.prevent
                          ><TextCell :draggable="isDragable" v-model:caption="store.tableData.rows[index_row].name" /></th>

                          <template v-for="(col, index_col) in store.tableData.cols" :key="[row,col]">
                            <DataCell :rowId="row.id" :colId="col.id"/>
                          </template>
                </tr>
            </tbody>
        </table>
        </div>`
}