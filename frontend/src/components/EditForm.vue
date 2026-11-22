<script setup>
import { reactive, watch } from 'vue'
import TimePicker from './TimePicker.vue'

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
    <div class="form-backdrop" @click.self="cancelEdit()">
        <section class="form-dialog" role="dialog" aria-modal="true" aria-label="Edit Entry">
            <h2>Edit Entry</h2>
            <form @submit.prevent="applyEdit()">
                <input v-model="form.id" type="hidden" />
                <label for="type">Type:</label>
                <select class="form-control" v-model="form.type" id="type" required>
                    <option value="start">Start</option>
                    <option value="stop">Stop</option>
                </select>
                <label for="date">Date:</label>
                <span id="date">{{ props.entry?.date.toLocaleDateString() }}</span>
                <label for="time">Time:</label>
                <TimePicker v-model="form.time" :show-seconds="false" />
                <div class="form-actions">
                    <button class="button" type="submit">Save</button>
                    <button class="button button-outline" type="button" @click="cancelEdit()">Cancel</button>
                </div>
            </form>
        </section>
    </div>
</template>

<style scoped>
.form-dialog h2 {
    margin-bottom: 1.25rem;
}

.form-dialog form {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    align-items: center;
    gap: 0.75rem;
}

.form-actions {
    grid-column: 1 / -1;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

</style>