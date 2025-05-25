  export default {
    props:{ title: String,
            dialog_url: String,
            },
    data(){
        return { dialogVisible: false,
                //title: 'Создание знания',
                resolvePromise: 0,
                //dialog_url : knowledge_create_url,
                }
    },
    mounted(){},
    updated() {
        //если это отображение формы
        if (this.dialogVisible) {
            //Загружаем поля формы
            this.loadData();

            // ставим хуки htmx
            htmx.process(this.$refs.dlg_form)

            //Ставим обработчик на смену
            htmx.on("htmx:beforeSwap", (e) => {
            // Empty response targeting #dialog => hide the modal
                if (e.detail.target.id == "dialog") {
                   if (e.detail.xhr.status == 201) {
                        e.detail.shouldSwap = false;
                        const data = JSON.parse(e.detail.xhr.response)
                        this.ok(data)
                   }
                }
            })
        }
    },
  methods:{
        loadData(){
          htmx.ajax('GET', this.dialog_url, { target: '#dialog' });
        },

        show() {
            this.dialogVisible=true
            this.close = 0;
            const dialogPromise = () => new Promise((resolve, reject) => this.resolvePromise = resolve);
            return dialogPromise()
        },

        close_dialog() {
            this.dialogVisible = false
            this.resolvePromise(false)
        },
        ok(value){
           this.dialogVisible = false
           this.resolvePromise(value)
        },
    },
  template: `
    <el-dialog v-model="dialogVisible" :title="title" width="80%" modal>
        <form id="dialog" ref="dlg_form" :hx-post="dialog_url" enctype="multipart/form-data">
        </form>
        <template #footer>
            <div class="dialog-footer">
               <el-button  type="primary" native-type="submit" form="dialog" size="large" >Сохранить</el-button>
               <el-button  size="large" @click="close_dialog">Отмена</el-button>
            </div>
    </template>
    </el-dialog>`
}