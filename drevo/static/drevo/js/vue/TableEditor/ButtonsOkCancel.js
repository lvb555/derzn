export default {
    props:["onSave", "SaveEnabled"],

    methods: {
        goPrev() {
         if (document.getElementById('prev')) {
            window.location = document.getElementById('prev').value
         }
         else
         { console.log('invalid prev value')}
        },
        doSave(){
            this.onSave();
        },
    },
  template: `
        <div class="d-flex justify-content-end align-items-center">
            <button class="btn btn-primary btn-lg m-2" :disabled="!SaveEnabled" @click="doSave" type="button">Сохранить</button>
            <button class="btn btn-secondary btn-lg m-2" @click="goPrev" type="button">Закрыть</button>
        </div>`
}