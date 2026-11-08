<script setup>

const props = defineProps({
    entries: Array
})

const emit = defineEmits(['edit', 'delete'])

</script>
<template>
    <table>
        <thead>
            <tr>
                <th>id</th>
                <th>type</th>
                <th>time</th>
                <th>action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="entry in entries" :key="entry.id">
                <td>{{ entry.id }}</td>
                <td>{{ entry.type }}</td>
                <td>{{ entry.getTime() }}</td>
                <td>
                    <button @click="() => emit('edit', entry.id)">Edit</button>
                    <button @click="() => emit('delete', entry.id)">Delete</button>
                </td>
            </tr>
        </tbody>
    </table>
</template>