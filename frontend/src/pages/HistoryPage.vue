<script setup>
import { ref, onMounted } from 'vue'
import { ApiInteractor } from '../js/ApiInteractor.js'
import { formatToday } from '../js/time.js'

const api = new ApiInteractor()

const history = ref([])
let currentHistorySize = history.value.length
let currentLast = formatToday()
let fullLength = -1

class HistoryItem {
    constructor(item) {
        this.date = new Date(item.date)
        this.worked = item.worked
        this.delta = item.delta
    }
}

const loadMore = async () => {
    const response = await api.getHistory(currentLast, 25)
    history.value = history.value.concat(response.history.map(item => new HistoryItem(item)))
    if (response.history.length > 0) {
        currentLast = response.history[response.history.length - 1].date
    }
    currentHistorySize = history.value.length
    fullLength = response.fullLength
    console.log(history.value)
}

// TODO: this might be moved to a separate utility file for consistency across the app and for translation purposes
const dayNames = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']

onMounted(loadMore)

</script>

<template>
    <div>
        <h1>History</h1>
        <div class="history-container">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Worked</th>
                        <th>Delta</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in history" :key="item.date">
                        <td>{{ dayNames[item.date.getDay()] }} {{ item.date.toLocaleDateString() }}</td>
                        <td>{{ item.worked }}</td>
                        <td>{{ item.delta }}</td>
                    </tr>
                    <tr v-if="currentHistorySize < fullLength">
                        <td colspan="3">
                            <button @click="loadMore">Load More</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.history-container {
    max-height: 70vh;
    overflow-y: auto;
}
</style>