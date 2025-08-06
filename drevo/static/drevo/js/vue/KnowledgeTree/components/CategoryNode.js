export default {
    template: `
        <div class="knowledge-tree">
            <div v-if="loading" class="loading">Загрузка дерева знаний...</div>

            <div class="tree-container">
                <div v-if="isRoot" class="children-container">
                    <div v-if="loadingChildren" class="loading">Загрузка...</div>

                    <template v-else>
                        <category-node
                            v-for="child in childCategories"
                            :key="'category-' + child.id"
                            :category="child"
                            :depth="0"
                            :fetch-params="fetchParams"
                            :margin="margin"
                        />

                        <div class="knowledge-list">
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

                        <div v-if="isLoadingMore" class="loading-more">
                            <span>Загрузка...</span>
                        </div>
                        <div class="scroll-sentinel" ref="sentinel"></div>
                    </template>
                </div>

                <template v-else>
                    <div class="category-node"  :data-id="category.id">
                        <div class="node-content-wrapper" :style="{'margin-left': depth * margin + 'px'}">
                            <div class="node-connector" v-if="depth > 0"></div>
                            <div class="category-header-wrapper">
                                <div
                                    class="category-header"
                                    @click="toggle"
                                    :class="{ 'is-open': isOpen }"
                                >
                                    <span class="toggle-icon" :class="{'is-open': isOpen}" v-if="hasChildren"></span>
                                    <span class="category-name">{{ category.name }}</span>
                                    <span
                                        class="children-count"
                                        v-if="category.children_count > 0"
                                        :data-count="category.children_count"
                                    >
                                        {{ category.children_count }}
                                    </span>
                                    <span
                                        class="knowledge-count"
                                        v-if="category.knowledge_count > 0"
                                        :data-count="category.knowledge_count"
                                    >
                                        {{ category.knowledge_count }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div v-if="isOpen" class="children-container" ref="childrenContainer">
                            <div v-if="loadingChildren" class="loading">Загрузка...</div>

                            <template v-else>
                                <category-node
                                    v-for="child in childCategories"
                                    :key="'category-' + child.id"
                                    :category="child"
                                    :depth="depth + 1"
                                    :fetch-params="fetchParams"
                                    :margin="margin"
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

                                <div v-if="isLoadingMore" class="loading-more">
                                    <span>Загрузка...</span>
                                </div>
                                <div class="scroll-sentinel" ref="sentinel"></div>
                            </template>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    `,

    props: {
        category: {
            type: Object,
            default: null
        },
        depth: {
            type: Number,
            default: -1
        },
        fetchParams: {
            type: Object,
            default: () => ({})
        },
        margin: {
            type: Number,
            default: 0
        },
        showUncategorized: {
            type: Boolean,
            default: true
        }
    },

    data() {
        return {
            isOpen: false,
            loading: this.depth === -1,
            loadingChildren: false,
            childCategories: [],
            knowledgeItems: [],
            loaded: false,
            currentPage: 1,
            hasMore: false,
            isLoadingMore: false,
            scrollObserver: null
        }
    },

    computed: {
        isRoot() {
            return this.depth === -1;
        },
        hasChildren() {
            if (this.isRoot) return true;
            return this.category.children_count > 0 || this.category.knowledge_count > 0;
        },
        requestParams() {
            const params = {
                ...this.fetchParams,
                page: this.currentPage
            };

            if (this.isRoot) {
                params.include_uncategorized = this.showUncategorized ? 'yes' : 'no';
            }

            return params;
        }
    },

    methods: {
        async toggle() {
            if (!this.isOpen) {
                this.isOpen = true;
                if (!this.loaded) {
                    await this.loadChildren();
                }
            } else {
                this.isOpen = false;
                this.destroyInfiniteScroll();
            }
        },

        async loadChildren(page = 1) {
            if (page === 1) {
                if (this.isRoot) {
                    this.loading = true;
                } else {
                    this.loadingChildren = true;
                }
                this.childCategories = [];
                this.knowledgeItems = [];
            } else {
                this.isLoadingMore = true;
            }

            try {
                const url = this.isRoot
                    ? '/api/categories/'
                    : `/api/categories/${this.category.id}/children/`;

                const response = await axios.get(url, {
                    params: this.requestParams
                });

                const data = response.data;

                if (page === 1) {
                    this.childCategories = data.results.categories || [];
                    this.knowledgeItems = data.results.knowledge || [];
                } else {
                    this.childCategories = [...this.childCategories, ...(data.results.categories || [])];
                    this.knowledgeItems = [...this.knowledgeItems, ...(data.results.knowledge || [])];
                }

                this.hasMore = !!data.next;
                this.currentPage = page;
                this.loaded = true;

                this.$nextTick(() => {
                    if ((this.isOpen || this.isRoot) && this.hasMore) {
                        this.setupInfiniteScroll();
                    }
                });
            } catch (error) {
                console.error('Ошибка загрузки:', error);
            } finally {
                this.loading = false;
                this.loadingChildren = false;
                this.isLoadingMore = false;
            }
        },

        setupInfiniteScroll() {
            this.destroyInfiniteScroll();

            this.$nextTick(() => {
                const container = this.isRoot
                    ? this.$el.querySelector('.tree-container > .children-container')
                    : this.$refs.childrenContainer;
                const sentinel = this.$refs.sentinel;

                if (!sentinel || !container) return;

                this.scrollObserver = new IntersectionObserver((entries) => {
                     entries.forEach(entry => {
                        if (entry.isIntersecting &&
                            entry.intersectionRatio > 0.5 && // Видно более 50% элемента
                            !this.isLoading &&
                            this.hasMore) {
                        this.loadChildren(this.currentPage + 1);
                        }
                    });
                    }, {
                    threshold: [0, 0.1, 0.5, 1], // Пороги видимости
                    rootMargin: '50px' // Загрузка начинается когда элемент в 50px от зоны видимости
                });

                this.scrollObserver.observe(sentinel);
            });
        },

        destroyInfiniteScroll() {
            if (this.scrollObserver) {
                this.scrollObserver.disconnect();
                this.scrollObserver = null;
            }
        }
    },

    watch: {
        isOpen(newVal) {
            if (newVal && this.hasMore) {
                this.$nextTick(() => {
                    this.setupInfiniteScroll();
                });
            } else {
                this.destroyInfiniteScroll();
            }
        },
        fetchParams: {
            deep: true,
            handler() {
                this.loadChildren(1);
            }
        },
        showUncategorized() {
            if (this.isRoot) {
                this.loadChildren(1);
            }
        }
    },

    created() {
        if (this.isRoot) {
            this.loadChildren();
        }
    },

    beforeDestroy() {
        this.destroyInfiniteScroll();
    }
};