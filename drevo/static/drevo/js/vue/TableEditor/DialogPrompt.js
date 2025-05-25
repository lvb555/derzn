  export default {
    close: 0,
    data(){
        return { dialogVisible: false,
                value:'',
                caption: 'Введите значение',
                title: 'Ввод'}
    },
  methods:{
        show(value) {
            this.value = value
            this.dialogVisible=true
            this.close = 0;
            //я не знаю почему, но только так удалось поставить фокус
            //autofocus не сработал, в хуках тоже не работает
            setTimeout(()=>{this.$refs.input_value.focus()}, 100);
            const dialogPromise = () => new Promise((resolve, reject) => this.close = resolve);
            return dialogPromise()
        },
        close_dialog() {
            //this.$refs.input_value.focus()
            this.close(false)
            this.dialogVisible = false
        },
        ok(){
            this.close(this.value)
            this.dialogVisible = false
        }
    },
  template: `
       <el-dialog v-model="dialogVisible" :title="title" width="500">
    <el-form>
      <el-form-item :label="caption">
        <el-input @keydown.enter.stop.prevent="ok" clearable v-model="value" ref="input_value" autocomplete="off" autofocus />
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="close_dialog">Отмена</el-button>
        <el-button type="primary" @click="ok">
          Ок
        </el-button>
      </div>
    </template>
  </el-dialog>`
}