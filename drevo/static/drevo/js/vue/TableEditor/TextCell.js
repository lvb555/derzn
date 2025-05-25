import {store} from './store.js'

export default {
    props: ['caption', 'source'],
    emits: ['update:caption'],
    data(){
        return {
            editing: false,
            store
        }
    },
    methods: {
        update: function (e) {
            this.editing = false
            this.$emit('update:caption', e.target.value)
            store.isChanged=true
        },
        onDblClick(e) {
            if (store.userPermissions.changeTableText) this.editing=true;
            if (this.source === 'group') return;

            if (store.selected.isNew()) this.editing=true;
        },
    },

template: `
<div class="text_cell" @dblclick="onDblClick">
    <textarea
      v-if="editing"
      :value="caption"
      @change="update"
      @blur="update"
      @keydown.esc="editing = false"
      @vue:mounted="({ el }) =>{ el.focus() }"
      placeholder="Введите название"
    />
    <p class="p-1" draggable="true" v-else>{{ caption }}</p>
  </div>`
}


