export default {
    template: `
        <div class="knowledge-list" :style="{'margin-left': depth * margin + 'px'}">
            <div
                v-for="item in items"
                :key="'knowledge-' + item.id"
                :href="item.url"
                class="knowledge-item"
                :class="{'is-selected': isCurrentKnowledge(item.id)}"
                @click.stop="selectKnowledge(item.id)"
            >
                <img :src="item.type_icon" class="knowledge-icon" alt="Тип">
                <span class="knowledge-type">{{ item.type_name }}</span>
                <span class="knowledge-icon" @click="handleGraphView(item.id)">🔍 </span>
                <a :href="item.url" class="knowledge-title">{{ item.name }}</a>
                <span class="knowledge-author" v-if="item.author">({{ item.author }})</span>
            </div>
        </div>
    `,
     inject: ['onItemSelected','getSelectedItems'],
    props: {
        items: Array,
        depth: Number,
        margin: Number,
        categoryId: [Number, String],
    },
    methods: {
        selectKnowledge(knowledgeId) {
           this.onItemSelected({
           type: 'knowledge',
           category: this.categoryId,
           id: knowledgeId,
        })
       },
       isCurrentKnowledge(itemId) {
            return itemId === this.getSelectedItems().knowledge
        },
        handleGraphView(knowledgeId) {
            let graph_url = `/drevo/knowledge/${knowledgeId}/graph`;
            window.open(graph_url, '_blank');
        }
    }

};