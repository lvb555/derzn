import ButtonsOkCancel from './ButtonsOkCancel.js'
import ButtonsTableEdit from './ButtonsTableEdit.js'
import ButtonsEditData from './ButtonsEditData.js'
import DataTable from './DataTable.js'
import TextCell from './TextCell.js'
import DataCell from './DataCell.js'
import DialogPrompt from './DialogPrompt.js'
import DialogCreate from './DialogCreate.js'
import DialogSelectKnowledge from './DialogSelectKnowledge.js'
import {store} from './store.js'
const { ElMessageBox, ElMessage } = ElementPlus

const app = Vue.createApp({
   data() {
        return {
                store,
                knowledge_create_url: knowledge_create_url,
                http: axios.create({
                            xsrfCookieName: 'csrftoken',
                            xsrfHeaderName: "X-CSRFTOKEN",
                            }),
        }},
   mounted() {
        store.tableData.group = headerData.group? headerData.group: ''
        store.tableData.group_col = headerData.group_col? headerData.group_col: ''
        store.tableData.group_row = headerData.group_row? headerData.group_row: ''
        store.userPermissions = userPermissions
        store.userLevel = userLevel
        if (headerData.cols&&headerData.cols.length)  store.tableData.cols = headerData.cols
        if (headerData.rows&&headerData.rows.length) store.tableData.rows = headerData.rows

        store.tableData.cells = new Map(Object.entries(tableData))
        store.isChanged = true
        console.log(store.permissions)
   },
  methods: {
    alert(message) {
         ElMessageBox.alert(message, 'Внимание', {autofocus: false, confirmButtonText: 'OK',})
         },
    prompt(message, callOk) {
       this.$refs.prompt.show(message)
       .then(text => {callOk(text)})
    },
    tryTextEdit(){
            const [rowId, colId ] = store.selected.elementId
            const cell = store.tableData.getCell(rowId, colId)

            if (cell.text) {
                if (!store.tableData.canChange(rowId, colId)) {
                console.log('Нет прав на редактирование')
                return
                }
            }
            else
            {
               if (!store.tableData.canFillEmpty(rowId, colId)) {
               console.log('Нет прав на заполнение')
               return
               }
            }

            if (cell.id) {
                this.alert("Для ввода текста в ячейку со знанием необходимо сначала очистить её")
                return
            }

            this.prompt(cell.text, (value) => {if (value)  store.tableData.setCellText(rowId, colId, value) })
    },
    createKnowledge() {
        if (!store.tableData.isCellFree()) {
            this.alert("Для изменения знания в непустой ячейке необходимо сначала очистить её")
            return
        }

        const [rowId, colId ] = store.selected.elementId
        if (!store.tableData.canFillEmpty(rowId, colId)) {
            console.log('Нет прав на заполнение')
            return
        }

        this.$refs.createKnowledge.show()
            .then(value => {
            if (value && store.selected.elementType=='d') {
                  store.tableData.setCell(rowId, colId, {id:value.id, text:value.name})
                }
            })
    },
    selectKnowledge() {
        if (!store.tableData.isCellFree()) {
            this.alert("Для изменения знания в непустой ячейке необходимо сначала очистить её")
            return
        }

        const [rowId, colId ] = store.selected.elementId
        if (!store.tableData.canFillEmpty(rowId, colId)) return

        this.$refs.selectKnowledge.show()
        .then(value => {
            if (value && store.selected.elementType=='d') {
                store.tableData.setCell(rowId, colId, {id:value.id, text:value.name})
            }
        })
    },
    onSave(){
        let data = {}
        data.group = this.store.tableData.group
        data.group_row = this.store.tableData.group_row
        data.group_col = this.store.tableData.group_col
        data.cols = this.store.tableData.cols
        data.rows = this.store.tableData.rows
        data.cells = {}
        this.store.tableData.cells.forEach((value, key) => {
            data.cells[key] = value;
            });
        // Нужно вручную установить Content-Type
        this.http.post('', data, { headers: { 'Content-Type': 'application/json' } })
        .then(function (response) {
            console.log(response.data.result);
            store.isChanged=false
            ElMessage({message: response.data.result, type: 'success', offset:140 })
        })
        .catch(function (error) {
            if (error.response && error.response.data.result) {
                console.log(error.response.data.result);
                ElMessage.error(error.response.data.result)
            }
            else{
                ElMessage.error('Ошибка при сохранении данных')
            }
        });
    },
},
template: `
<div>
    <div class="row mb-5">
        <div class="col"><DataTable/></div>
    </div>
    <div class="row mb-3">
        <div class="col-4"><ButtonsTableEdit/></div>
        <div class="col-4"><ButtonsEditData/></div>
        <div class="col-4"><ButtonsOkCancel :onSave="onSave" :SaveEnabled="store.isChanged"  /> </div>
    </div>

    <div class="row mb-5">
        <div v-show="false" class="col">
            <p>isChanged={{ store.isChanged }}</p>
            <p>selected={{ store.selected.elementType}} , {{store.selected.elementId }}</p>
            <p>cols={{store.tableData.cols}}</p>
            <p>rows={{store.tableData.rows}}</p>
            <p>cells={{store.tableData.cells}}</p>
        </div>
        <DialogPrompt ref='prompt' />
        <DialogCreate ref='createKnowledge' title="Создание знания" :dialog_url="knowledge_create_url" />
        <DialogSelectKnowledge ref='selectKnowledge' />
    </div>
    <footer>
        <div class="row">

        </div>
    </footer>
</div>
 `
});

app.use(ElementPlus);
app.component('ButtonsOkCancel', ButtonsOkCancel)
app.component('ButtonsTableEdit', ButtonsTableEdit)
app.component('ButtonsEditData', ButtonsEditData)
app.component('DataTable', DataTable)
app.component('TextCell', TextCell)
app.component('DataCell', DataCell)
app.component('DialogPrompt', DialogPrompt)
app.component('DialogCreate', DialogCreate)
app.component('DialogSelectKnowledge', DialogSelectKnowledge)
store.app = app.mount('#app');
