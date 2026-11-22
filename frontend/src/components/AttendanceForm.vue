<script setup>
import { ref } from 'vue'

const emit = defineEmits(['updated'])

const showDialog = ref(false)
const modelValue = defineModel({ type: String })

</script>


<template>
    <div class="attendance-value" :class="{ invalid: modelValue === 'undefined' }" @click="showDialog = true">
        {{ modelValue }}
    </div>
    <div v-if="showDialog" class="form-backdrop" @click.self="showDialog = false; emit('updated')">
        <section class="form-dialog form-dialog--compact attendance-dialog" role="dialog" aria-modal="true"
            aria-label="Edit Attendance">
            <select class="form-control attendance-select" v-model="modelValue">
                <option value="in office">in_office</option>
                <option value="remote">remote</option>
                <option value="sick">sick</option>
                <option value="vacation">vacation</option>
                <option value="undefined" disabled>undefined</option>
            </select>
            <button class="button" @click="showDialog = false; emit('updated')">OK</button>
        </section>
    </div>
</template>

<style scoped>
.attendance-dialog {
    width: min(18rem, 100%);
}

.attendance-select {
    width: 100%;
}

.attendance-value {
    grid-column: 2;
    padding: 0.5rem 0.65rem;
    border: 1px solid var(--border);
    border-radius: 0.375rem;
    color: var(--text-h);
    cursor: pointer;
}

.attendance-value.invalid {
    border-color: #dc2626;
    color: #dc2626;
}

.attendance-value:hover {
    background: var(--code-bg);
}
</style>