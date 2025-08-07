export default {
    template: `
        <category-node
            :fetch-params="fetchParams"
            :show-uncategorized="showUncategorized"
        />
    `,

    data() {
        return {
            showUncategorized: true,
            filterPublished: true,
            filterSystem: false,
            selectedKnowledge: null, // ID выбранного знания
            selectedCategory: null   // ID выбранной категории
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
    provide() {
    return {
        onItemSelected: this.handleItemSelected,
        getSelectedItems: () => ({
            knowledge: this.selectedKnowledge,
            category: this.selectedCategory
        }),
        setSelectedKnowledge: (id) => { this.selectedKnowledge = id },
        setSelectedCategory: (id) => { this.selectedCategory = id }
        }
    },
    methods: {
        toParam(value) {
            if (value === true) return 'yes';
            if (value === false) return 'no';
            return 'all';
        },
       handleItemSelected(item) {
            console.log('Selected item from any level:', item)
            if (item.type == 'category'){
                this.selectedCategory = item.id;
            }
            else {
               this.selectedKnowledge = item.id;
            }
       },
    }
};