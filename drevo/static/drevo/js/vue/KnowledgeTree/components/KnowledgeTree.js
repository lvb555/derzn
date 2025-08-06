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

    methods: {
        toParam(value) {
            if (value === true) return 'yes';
            if (value === false) return 'no';
            return 'all';
        }
    }
};