//import { createApp } from 'vue';
import CategoryNode from './components/CategoryNode.js'
import KnowledgeTree from './components/KnowledgeTree.js';


const app = Vue.createApp({
    template: '<knowledge-tree />',
//    components: {
//        'category-node': CategoryNode,
//        'knowledge-tree': KnowledgeTree,
//
//    }
});

app.component('category-node', CategoryNode)
app.component('knowledge-tree', KnowledgeTree)

app.mount('#knowledge-tree-app');