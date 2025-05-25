    export default {
        data(){
        return { dialogVisible: false,
                value: '',
                title: 'Выберите знание',
                loading: false,
                resolvePromise: 0,
                options: []}
    },
    mounted() {
        this.options = []
    },
  methods:{
        remoteMethod(query) {
              this.loading = true;
              this.$root.http.get(`/drevo/search/knowledge_by_name?query=${query}`)
                    .then(response =>{
                        this.options = response.data.map( (item)=>{ return {label: item.name, value: item} })
                        this.loading = false;})
        },
        show(value) {
            this.value = value
            this.dialogVisible=true


            const dialogPromise = () => new Promise((resolve, reject) => this.resolvePromise = resolve);
            return dialogPromise()
        },
        close_dialog() {
            this.resolvePromise(false)
            this.dialogVisible = false
        },
        ok(){
            this.resolvePromise(this.value)
            this.dialogVisible = false
        }

    },
  template: `
       <el-dialog v-model="dialogVisible" :title="title" width="80%">

    <el-select-v2
        filterable
        v-model="value"
        label='name'
        value='id'
        value-key="id"
        no-match-text="Нет данных"
        clearable
        remote
        :remoteMethod='remoteMethod'
        :options="options"
        :loading="loading"
        placeholder="Выберите знание..."
        size="large"
        style="width: 80%">
     </el-select-v2>
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