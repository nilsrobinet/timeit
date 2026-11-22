<script setup>
import { onMounted, ref } from 'vue'

const errors = ref([])

import { ApiInteractor } from '../js/ApiInteractor'
const api = new ApiInteractor()

onMounted(() => {
    api.getErrorList().then(e => errors.value = e)
})
</script>

<template>
    <ul v-if="errors.length" class="error-list">
        <li v-for="e in errors" :key="e">{{ e }}</li>
    </ul>

</template>

<style scoped>
.error-list {
    color: red;
    height: 10vh;
    overflow: auto;
}

.error-list li {
    margin-bottom: 4px;
}
</style>