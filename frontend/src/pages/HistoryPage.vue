<script setup>
import { ref, onMounted } from 'vue'
import AttendanceForm from '../components/AttendanceForm.vue'
const attendance = ref([])
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
        this.attendance = item.attendance
    }

    hasValidAttendance() {
        return this.attendance.toLowerCase() !== 'undefined'
    }
}

const loadMore = async () => {
    const response = await api.getDaysSummary(currentLast, 25)

    console.log(response.history)

    history.value = history.value.concat(response.history.map(item => new HistoryItem(item)))
    if (response.history.length > 0) {
        currentLast = response.history[response.history.length - 1].date
    }
    currentHistorySize = history.value.length
    fullLength = response.fullLength
}

// TODO: this might be moved to a separate utility file for consistency across the app and for translation purposes
const dayNames = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
onMounted(loadMore)

</script>

<template>
    <section class="content-page history-page">
        <h1>History</h1>
        <div class="history-container">
            <table class="data-table history-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Worked</th>
                        <th>Delta</th>
                        <th>Attendance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in history" :key="item.date">
                        <td>{{ dayNames[item.date.getDay()] }} {{ item.date.toLocaleDateString() }}</td>
                        <td>{{ item.worked }}</td>
                        <td>{{ item.delta }}</td>
                        <td>
                            <AttendanceForm v-model="item.attendance"
                                @updated="api.setAttendance(item.date, item.attendance)" />
                        </td>
                    </tr>
                    <tr v-if="currentHistorySize < fullLength">
                        <td colspan="4" class="history-load-more-cell">
                            <button class="button button-outline" @click="loadMore">Load More</button>
                        </td>
                    </tr>

                </tbody>
                <button @click="loadMore">Load More</button>
            </table>
        </div>
    </section>
</template>

<style scoped>
.history-container {
    max-height: 70vh;
    overflow: auto;
    border-block: 1px solid var(--border);
}

.history-table {
    min-width: 36rem;
}

.history-table th {
    position: sticky;
    top: 0;
    background: var(--code-bg);
}

.history-load-more-cell {
    text-align: center;
}
</style>