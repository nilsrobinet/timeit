<script setup>
import { ref, watch } from 'vue'

const emit = defineEmits(['update:modelValue'])

const showDialog = ref(false)

const props = defineProps({
    modelValue: Date,
    showSeconds: Boolean
})
const time = ref(props.modelValue)

const seconds = ref(0)
const minutes = ref(0)
const hours = ref(0)

let tsplit = time.value.split(':')

seconds.value = tsplit[2]
minutes.value = tsplit[1]
hours.value = tsplit[0]
console.log("time", time.value, hours.value, minutes.value, seconds.value)

function updateTimeEvent(hours, minutes, seconds) {
    emit('update:modelValue', `${hours}:${minutes}:${seconds}`);
}

watch([hours, minutes, seconds], () => updateTimeEvent(hours.value, minutes.value, seconds.value))


</script>


<template>
    <div class="time-picker-value" @click="showDialog = true">
        {{ hours }}:{{ minutes }}<span v-if="props.showSeconds">:{{ seconds }}</span>
    </div>
    <div v-if="showDialog" class="form-backdrop" @click.self="showDialog = false">
        <section class="form-dialog form-dialog--compact" role="dialog" aria-modal="true" aria-label="Edit Entry">
            <h2>HH:MM<span v-if="props.showSeconds">:SS</span></h2>
            <input class="form-control time-picker-input" type="number" v-model="hours" min="0" max="23">
            <span>:</span>
            <input class="form-control time-picker-input" type="number" v-model="minutes" min="0" max="59">
            <span v-if="props.showSeconds">:</span>
            <input v-if="props.showSeconds" class="form-control time-picker-input" type="number" v-model="seconds" min="0" max="59">
            <button class="button" @click="showDialog = false">OK</button>
        </section>
    </div>
</template>

<style scoped>
.time-picker-input {
    width: 4rem;
}

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
</style>