<script setup>
import { computed, ref } from 'vue'

const emit = defineEmits(['updated'])

const showDialog = ref(false)
const modelValue = defineModel({ type: String })
const statusLabels = {
    in_office: 'In office',
    remote: 'Remote',
    sick: 'Sick',
    vacation: 'Vacation',
    undefined: 'Not set'
}
const displayStatus = computed(() => statusLabels[modelValue.value] ?? modelValue.value ?? 'Not set')

</script>


<template>
    <button
        type="button"
        class="attendance-value"
        :class="{ invalid: modelValue === 'undefined' }"
        :aria-expanded="showDialog"
        :aria-label="modelValue === 'undefined' ? 'Attendance not set; edit attendance' : 'Edit attendance: ' + displayStatus"
        aria-haspopup="dialog"
        @click="showDialog = true"
    >
        {{ displayStatus }}
    </button>
    <div v-if="showDialog" class="form-backdrop" @click.self="showDialog = false; emit('updated')">
        <section class="form-dialog form-dialog--compact attendance-dialog" role="dialog" aria-modal="true"
            aria-label="Edit Attendance">
            <h2>Attendance</h2>
            <select class="form-control attendance-select" v-model="modelValue">
                <option value="in_office">In office</option>
                <option value="remote">Remote</option>
                <option value="sick">Sick</option>
                <option value="vacation">Vacation</option>
                <option value="undefined" disabled>Not set</option>
            </select>
            <button class="button button-accent" @click="showDialog = false; emit('updated')">Save</button>
        </section>
    </div>
</template>

<style scoped>
.attendance-dialog {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.75rem;
    width: min(20rem, 100%);
}

.attendance-dialog h2 {
    grid-column: 1 / -1;
    margin: 0;
    font-size: 1.2rem;
}

.attendance-select {
    width: 100%;
    min-width: 0;
}

.attendance-value {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: min(100%, 18rem);
    min-height: 2.5rem;
    padding: 0.4rem 0.6rem;
    border: 1px solid var(--border);
    border-radius: 0.35rem;
    background: var(--bg);
    color: var(--text-h);
    text-align: left;
    cursor: pointer;
    box-sizing: border-box;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

.attendance-value::after {
    width: 0.35rem;
    height: 0.35rem;
    margin: -0.15rem 0 0 0.5rem;
    border-right: 1px solid currentColor;
    border-bottom: 1px solid currentColor;
    content: '';
    transform: rotate(45deg);
}

.attendance-value.invalid {
    border-color: var(--danger);
    background: var(--danger-bg);
    color: var(--danger);
    font-weight: 600;
}

.attendance-value:hover {
    background: var(--code-bg);
    border-color: var(--accent);
}

.attendance-value.invalid:hover {
    border-color: var(--danger);
    background: var(--danger-bg);
}
</style>