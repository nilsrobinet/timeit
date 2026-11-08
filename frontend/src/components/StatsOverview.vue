<script setup>
import { ref } from 'vue'
import { FDuration, getDateDurationDelta } from '../js/time.js'

const props = defineProps({
    summary: Object
})

const currentWorked = ref(new FDuration(props.summary.worked))

function updateCurrentWorked(newWorked) {
    if (props.summary.lastEntry.type === 'start') {
        const deltaAdder = getDateDurationDelta(new Date(props.summary.lastEntry.date), new Date())
        currentWorked.value = props.summary.worked.delta(deltaAdder)
    } else {
        currentWorked.value = props.summary.worked
    }
}
setInterval(() => {
    updateCurrentWorked(props.summary.worked)
}, 1000)



</script>

<template>
    <h1>
        <span id="worked">{{ currentWorked.toString() }}</span>
        /
        <span id="target">{{ summary.target.toString() }}</span>
    </h1>
    <div>
        <span id="day">Day+/-:<strong>{{ summary.day.toString() }}</strong></span>
        <span id="weekly">Week+/-:<strong>{{ summary.weekly.toString() }}</strong></span>
        <span id="total">Total+/-:<strong>{{ summary.total.toString() }}</strong></span>
    </div>
</template>