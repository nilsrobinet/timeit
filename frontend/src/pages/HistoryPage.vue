<script setup>
import { ref, onMounted } from 'vue'
import AttendanceForm from '../components/AttendanceForm.vue'
import { ApiInteractor } from '../js/ApiInteractor.js'
import { formatToday } from '../js/time.js'

const api = new ApiInteractor()

const history = ref([])
const fullLength = ref(0)
let currentLast = formatToday()

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
    fullLength.value = response.full_length
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
                        <td data-label="Date">{{ dayNames[item.date.getDay()] }} {{ item.date.toLocaleDateString() }}
                        </td>
                        <td data-label="Worked">{{ item.worked }}</td>
                        <td data-label="Delta">{{ item.delta }}</td>
                        <td data-label="Attendance">
                            <AttendanceForm v-model="item.attendance"
                                @updated="api.setAttendance(item.date, item.attendance)" />
                        </td>
                    </tr>
                    <tr v-if="history.length < fullLength" class="history-load-more-row">
                        <td colspan="4" class="history-load-more-cell">
                            <button class="button button-outline" @click="loadMore">Load More</button>
                        </td>
                    </tr>

                </tbody>
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

@media (max-width: 600px) {
    .history-container {
        max-height: none;
        overflow: visible;
        border: 0;
    }

    .history-table {
        min-width: 0;
    }

    .history-table thead {
        position: absolute;
        width: 1px;
        height: 1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
    }

    .history-table tbody {
        display: grid;
        gap: 0.75rem;
    }

    .history-table tbody tr:not(.history-load-more-row) {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.75rem;
        padding: 0.8rem;
        border: 1px solid var(--border);
        border-radius: 0.35rem;
    }

    .history-table tbody td {
        min-width: 0;
        padding: 0;
        border: 0;
        font-size: 0.85rem;
        overflow-wrap: anywhere;
    }

    .history-table tbody td::before {
        content: attr(data-label);
        color: var(--text);
        font-size: 0.7rem;
        font-weight: 600;
    }

    .history-table .history-load-more-row {
        display: block;
    }

    .history-table .history-load-more-cell {
        display: block;
        padding: 0.5rem 0;
        border: 0;
    }

    .history-table .history-load-more-cell::before {
        content: none;
    }
}
</style>