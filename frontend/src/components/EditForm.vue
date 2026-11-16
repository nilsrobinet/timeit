<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
    entry: Object
})

const form = reactive({ id: null, type: '', time: '' })

watch(() => props.entry, (entry) => {
    form.id = entry?.id ?? null
    form.type = entry?.type ?? ''

    const date = entry?.date
    form.time = date
        ? `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
        : ''
}, { immediate: true })


const emit = defineEmits(['save'])

function applyEdit() {
    if (props.entry && props.entry?.id == form.id) {
        props.entry.date.setHours(Number(form.time.split(':')[0]))
        props.entry.date.setMinutes(Number(form.time.split(':')[1]))
        props.entry.date.setSeconds(Number(form.time.split(':')[2]))
        props.entry.type = form.type
    }
    emit('save', props.entry)
}

</script>

<template>
    <h2>Edit Entry</h2>
    <form @submit.prevent="applyEdit()">
        <input v-model="form.id" type="hidden" />
        <label for="type">Type:</label>
        <input v-model="form.type" id="type" type="text" />
        <label for="date">Date:</label>
        <span id="date">{{ props.entry?.date.toLocaleDateString() }}</span>
        <label for="time">Time:</label>
        <input v-model="form.time" id="time" type="time" step="1" required />
        <button type="submit">Save</button>
    </form>
</template>