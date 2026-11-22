<script setup>

defineProps({
    entries: Array
})

const emit = defineEmits(['edit', 'delete'])

</script>
<template>
    <p v-if="entries.length === 0" class="empty-state">No entries recorded for this date.</p>
    <div v-else class="entry-list-container">
        <table class="data-table entry-list">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Time</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="entry in entries" :key="entry.id">
                    <td>{{ entry.type }}</td>
                    <td>{{ entry.getTime() }}</td>
                    <td>
                        <button class="button button-quiet entry-action" @click="() => emit('edit', entry)">Edit</button>
                        <button class="button button-quiet entry-action" @click="() => emit('delete', entry.id)">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style scoped>
.entry-list-container {
    overflow-x: auto;
}

.empty-state {
    margin: 0;
    padding: 1.25rem 0;
    border-top: 1px solid var(--border);
    color: var(--text);
}

.entry-list td:last-child {
    text-align: right;
    white-space: nowrap;
}

.entry-action {
    margin-left: 0.4rem;
}

@media (max-width: 480px) {
    .entry-list {
        table-layout: fixed;
    }

    .entry-list th,
    .entry-list td {
        padding: 0.6rem 0.35rem;
    }

    .entry-list th:last-child,
    .entry-list td:last-child {
        width: 35%;
        text-align: center;
    }

    .entry-action + .entry-action {
        margin-left: 0.2rem;
    }
}
</style>