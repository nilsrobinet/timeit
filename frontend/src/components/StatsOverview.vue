<script setup>

const props = defineProps({
    summary: Object
})

</script>

<template>
    <h1>
        <span id="worked">{{ summary.worked.toString() }}</span>
        /
        <span id="target">{{ summary.target.toString() }}</span>
    </h1>
    <div>
        <span id="day">Day+/-:<strong>{{ summary.day.toString() }}</strong></span>
        <span id="weekly">Week+/-:<strong>{{ summary.weekly.toString() }}</strong></span>
        <span id="total">Total+/-:<strong>{{ summary.total.toString() }}</strong></span>
    </div>
</template>