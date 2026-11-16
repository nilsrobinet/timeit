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


const emit = defineEmits(['save', 'cancel'])

function applyEdit() {
    if (props.entry && props.entry?.id == form.id) {
        props.entry.date.setHours(Number(form.time.split(':')[0]))
        props.entry.date.setMinutes(Number(form.time.split(':')[1]))
        props.entry.date.setSeconds(Number(form.time.split(':')[2]))
        props.entry.type = form.type
    }
    emit('save', props.entry)
}

function cancelEdit() {
    emit('cancel')
}

</script>

<template>
    <div class="form-backdrop edit-form-backdrop" @click.self="cancelEdit()">
        <section class="form-dialog" role="dialog" aria-modal="true" aria-label="Edit Entry">
            <h2>Edit Entry</h2>
            <form @submit.prevent="applyEdit()">
                <input v-model="form.id" type="hidden" />
                <label for="type">Type:</label>
                <select v-model="form.type" id="type" required>
                    <option value="start">Start</option>
                    <option value="stop">Stop</option>
                </select>
                <label for="date">Date:</label>
                <span id="date">{{ props.entry?.date.toLocaleDateString() }}</span>
                <label for="time">Time:</label>
                <input v-model="form.time" id="time" type="time" step="1" required />
                <button type="submit">Save</button>
                <button type="button" @click="cancelEdit()">Cancel</button>
            </form>
        </section>
    </div>
</template>

<style scoped>
.form-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: grid;
    place-items: center;
    background: rgb(0 0 0 / 50%);
}

.form-dialog {
    padding: 1.5rem;
    background: white;
}
</style>