<script setup>
import { ref, watch } from 'vue'
import PaddedNumberInput from './PaddedNumberInput.vue'

const emit = defineEmits(['update:modelValue'])

const showDialog = ref(false)

const props = defineProps({
    modelValue: Date,
    showSeconds: Boolean,
    disabled: Boolean
})
const time = ref(props.modelValue)

const seconds = ref(0)
const minutes = ref(0)
const hours = ref(0)

if (!time.value) { time.value = "00:00:00" }
let tsplit = time.value.split(':')

seconds.value = tsplit[2]
minutes.value = tsplit[1]
hours.value = tsplit[0]

function padTimePart(value) {
    return String(value ?? '0').padStart(2, '0')
}

if (seconds.value !== undefined) seconds.value = padTimePart(seconds.value)
minutes.value = padTimePart(minutes.value)
hours.value = padTimePart(hours.value)

function updateTimeEvent(hours, minutes, seconds) {
    if (!seconds) {
        emit('update:modelValue', `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`);
    } else {
        emit('update:modelValue', `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`);
    }
}

watch([hours, minutes, seconds], () => updateTimeEvent(hours.value, minutes.value, seconds.value))


</script>


<template>
    <div class="time-picker-value" @click="showDialog = true && !props.disabled" :class="{ disabled: props.disabled }">
        {{ padTimePart(hours) }}:{{ padTimePart(minutes) }}<span v-if="props.showSeconds">:{{ padTimePart(seconds)
            }}</span>
    </div>
    <div v-if="showDialog" class="form-backdrop" @click.self="showDialog = false">
        <section class="form-dialog form-dialog--compact" role="dialog" aria-modal="true" aria-label="Edit Entry">
            <h2>HH:MM<span v-if="props.showSeconds">:SS</span></h2>
            <PaddedNumberInput v-model="hours" label="Hours" :min="0" :max="23" />
            <span>:</span>
            <PaddedNumberInput v-model="minutes" label="Minutes" :min="0" :max="59" />
            <template v-if="props.showSeconds">
                <span>:</span>
                <PaddedNumberInput v-model="seconds" label="Seconds" :min="0" :max="59" />
            </template>
            <button class="button" @click="showDialog = false">OK</button>
        </section>
    </div>
</template>

<style scoped>
.time-picker-value {
    grid-column: 2;
    padding: 0.5rem 0.65rem;
    border: 1px solid var(--border);
    border-radius: 0.375rem;
    color: var(--text-h);
    cursor: pointer;
}

.time-picker-value:hover {
    background: var(--code-bg);
}

.time-picker-value.disabled {
    background: var(--code-bg);
    color: var(--text-s);
}
</style>