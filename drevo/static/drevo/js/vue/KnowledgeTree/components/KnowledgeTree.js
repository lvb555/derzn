export default {
    template: `
        <div class="knowledge-tree">
            <div v-if="loading" class="loading">Загрузка дерева знаний...</div>

            <div class="tree-container">
                <!-- Дерево категорий -->
                <category-node
                    v-for="category in rootCategories"
                    :key="'category-' + category.id"
                    :category="category"
                    :depth="0"
                    :fetch-params="fetchParams"
                />
            </div>
        </div>
    `,

    data() {
        return {
            loading: true,
            rootCategories: [],
            showUncategorized: true,
            filterPublished : true,
            filterSystem: false,
        }
    },
    computed: {
    fetchParams() {
      return {
        published: this.toParam(this.filterPublished),
        system: this.toParam(this.filterSystem),
      }
    }
  },
    async created() {
        await this.loadRootCategories();
        this.loading = false;
    },

    methods: {
        toParam(value) { // true/false/null → yes/no/all
            if (value === true) return 'yes'
            if (value === false) return 'no'
            return 'all'
        },
        async loadRootCategories() {
            try {
                let params = this.fetchParams
                if (this.showUncategorized) {
                    params.include_uncategorized = 'yes';
                }
                const response = await axios.get('/api/categories/', {params: this.fetchParams});
                this.rootCategories = response.data.categories;
            } catch (error) {
                console.error('Ошибка загрузки корневых категорий:', error);
            }
        },
    }
};