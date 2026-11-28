<script setup>
const emit = defineEmits(['update:modelValue'])
const props = defineProps({
    modelValue: [String, Number],
    label: String,
    min: { type: Number, default: 0 },
    max: Number,
    step: { type: Number, default: 1 },
    padding: { type: Number, default: 2 }
})

function updateValue(event) {
    const input = event.currentTarget
    const digits = input.value.replace(/\D/g, '').slice(0, props.padding)

    if (digits && (Number(digits) < props.min || Number(digits) > props.max)) {
        input.value = String(props.modelValue ?? '')
        return
    }

    input.value = digits
    emit('update:modelValue', digits)
}

function padValue() {
    emit('update:modelValue', String(props.modelValue ?? '').padStart(props.padding, '0'))
}

function stepValue(direction) {
    const value = Number(props.modelValue)
    const currentValue = Number.isInteger(value) ? value : props.min
    const steppedValue = Math.min(Math.max(currentValue + direction * props.step, props.min), props.max)
    emit('update:modelValue', String(steppedValue).padStart(props.padding, '0'))
}
</script>

<template>
    <div class="time-picker-controls">
        <input class="form-control time-picker-input" type="text" inputmode="numeric" pattern="[0-9]*"
            :maxlength="props.padding" :value="props.modelValue" :aria-label="props.label" @input="updateValue"
            @blur="padValue">
        <div class="time-picker-steppers">
            <button type="button" :aria-label="`Increase ${props.label}`" @click="stepValue(1)">&#9650;</button>
            <button type="button" :aria-label="`Decrease ${props.label}`" @click="stepValue(-1)">&#9660;</button>
        </div>
    </div>
</template>

<style scoped>
.time-picker-input {
    width: 4rem;
    padding-right: 1.4rem;
}

.time-picker-controls {
    display: inline-flex;
    align-items: center;
}

.time-picker-steppers {
    display: flex;
    flex-direction: column;
    margin-left: -1.35rem;
    z-index: 1;
}

.time-picker-steppers button {
    width: 1.2rem;
    height: 1rem;
    padding: 0;
    border: 0;
    background: transparent;
    color: var(--text-h);
    cursor: pointer;
    font-size: 0.55rem;
    line-height: 1;
}
</style>