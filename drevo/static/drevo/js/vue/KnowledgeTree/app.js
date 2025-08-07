//import { createApp } from 'vue';
import CategoryNode from './components/CategoryNode.js'
import KnowledgeTree from './components/KnowledgeTree.js';
import KnowledgeList from './components/KnowledgeList.js'

const app = Vue.createApp({
    template: '<knowledge-tree />',
});

app.component('knowledge-list', KnowledgeList)
app.component('category-node', CategoryNode)
app.component('knowledge-tree', KnowledgeTree)

app.mount('#knowledge-tree-app');