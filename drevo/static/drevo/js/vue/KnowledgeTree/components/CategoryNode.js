export default {
    template: `
        <div class="category-node">
            <div class="node-content-wrapper" :style="{'margin-left': depth * margin + 'px'}">
                <div class="node-connector" v-if="depth > 0"></div>
                <div class="category-header-wrapper" :class="{'root-category': depth === 0}">
                    <div class="category-header" @click="toggle" :class="{ 'is-open': isOpen }">
                        <span class="toggle-icon" v-if="hasChildren">
                            {{ isOpen ? '▼' : '►' }}
                        </span>
                        <span class="category-name">{{ category.name }}</span>
                        <span class="children-count" v-if="category.children_count > 0"
                            :data-count="category.children_count">
                            {{ category.children_count }}
                        </span>
                        <span class="knowledge-count" v-if="category.knowledge_count > 0"
                            :data-count="category.knowledge_count">
                            {{ category.knowledge_count }}
                        </span>
                    </div>
                </div>
            </div>

            <div v-if="isOpen" class="children-container">
                <!-- Текст загрузки появляется ТОЛЬКО после открытия -->
                <div v-if="loadingChildren" class="loading">Загрузка...</div>

                <template v-else>
                    <category-node
                        v-for="child in childCategories"
                        :key="'category-' + child.id"
                        :category="child"
                        :depth="depth + 1"
                        :fetch-params="fetchParams"
                    />

                    <div class="knowledge-list" :style="{'margin-left': (depth + 1) * margin + 'px'}">
                        <a
                            v-for="item in knowledgeItems"
                            :key="'knowledge-' + item.id"
                            :href="item.url"
                            class="knowledge-item"
                        >
                            <img :src="item.type_icon" class="knowledge-icon" alt="Тип">
                            <span class="knowledge-type">{{ item.type_name }}</span>
                            <span class="knowledge-title">{{ item.name }}</span>
                            <span class="knowledge-author" v-if="item.author">({{ item.author }})</span>
                        </a>
                    </div>
                </template>
            </div>
        </div>
    `,

    props: {
        category: {
            type: Object,
            required: true
        },
        depth: {
            type: Number,
            default: 0
        },
        fetchParams: {
            type: Object,
            default: () => ({})
        },
        margin: {
            type: Number,
            default: 0,
        },
    },

    data() {
        return {
            isOpen: false,
            loadingChildren: false,
            childCategories: [],
            knowledgeItems: [],
            loaded: false
        }
    },

    computed: {
        hasChildren() {
            return this.category.children_count > 0 || this.category.knowledge_count > 0;
        }
    },

    methods: {
        async toggle() {
            if (!this.isOpen) {
                this.isOpen = true; // Сначала открываем
                if (!this.loaded) {
                    await this.loadChildren(); // Затем загружаем
                }
            } else {
                this.isOpen = false;
            }
        },

        async loadChildren() {
            this.loadingChildren = true;
            try {
                const response = await axios.get(`/api/categories/${this.category.id}/children/`, {
                    params: this.fetchParams
                });
                this.childCategories = response.data.categories;
                this.knowledgeItems = response.data.knowledge;
                this.loaded = true;
            } catch (error) {
                console.error('Ошибка загрузки:', error);
            } finally {
                this.loadingChildren = false;
            }
        }
    }
};