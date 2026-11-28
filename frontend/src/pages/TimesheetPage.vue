<script setup>
import { ref } from 'vue'
import { FDuration, FDate, formatToday } from '../js/time.js'
import { ApiInteractor } from '../js/ApiInteractor.js'
import TimeKeepingEntry from '../js/TimeKeepingEntry.js'
import StatsOverview from '../components/StatsOverview.vue'
import DayEntryList from '../components/EntryList.vue'
import EditForm from '../components/EditForm.vue'
import AttendanceForm from '../components/AttendanceForm.vue'

const api = new ApiInteractor()

const currentDateStr = ref(formatToday())
const isStarted = ref(false)
const showEditForm = ref(false)
const editingEntry = ref(null)
const summary = ref({
    date: new FDate(new Date()),
    worked: new FDuration('+0:00:00'),
    target: new FDuration('+8:00:00'),
    day: new FDuration('+0:00:00'),
    weekly: new FDuration('+0:00:00'),
    total: new FDuration('+0:00:00'),
    avg_attendance: 0.0
})

function refreshSummary() {
    api.getSummary(currentDateStr.value).then(data => {
        summary.value = data
        isStarted.value = data.lastEntry?.type === 'start'
    })
}

const thisDayEntries = ref([])
const attendance = ref('undefined')
function refreshEntries() {
    api.getDay(currentDateStr.value).then(data => {
        thisDayEntries.value = data.entries.map(entry => new TimeKeepingEntry(entry))
        attendance.value = data.attendance
    })
}

function deleteEntry(id) {
    api.deleteEntry(id, currentDateStr.value).then(() => {
        thisDayEntries.value = thisDayEntries.value.filter(entry => entry.id !== id)
        refreshSummary()
    })
}

function editEntry(entry) {
    showEditForm.value = true
    editingEntry.value = entry
}

function checkInOut() {
    let type = isStarted.value ? 'stop' : 'start'
    let timestamp = currentDateStr.value == formatToday() ? null : currentDateStr.value + 'T00:00:00'
    console.log(timestamp)
    api.addEntry(currentDateStr.value, type, timestamp).then(() => {
        refreshSummary()
        refreshEntries()
    })
}

function saveEntry(entry) {
    showEditForm.value = false
    api.editEntry(entry).then(() => {
        refreshEntries()
        refreshSummary()
    })
}

function onDateChange() {
    refreshSummary()
    refreshEntries()
}

function getButtonText() {
    if (currentDateStr.value != formatToday()) {
        return 'Add Entry'
    }
    return isStarted.value ? 'Check Out' : 'Check In'
}

refreshSummary()
refreshEntries()

</script>

<template>
    <section class="content-page timesheet-page">
        <section class="timesheet-focus">
            <div class="timesheet-date">
                <input id="timesheet-date" class="form-control" v-model="currentDateStr" type="date"
                    @change="onDateChange" />
            </div>
            <StatsOverview :summary="summary" :do-live-update="currentDateStr == formatToday()" />
            <button class="button button-accent primary-button" @click="checkInOut">{{ getButtonText() }}</button>
            <AttendanceForm v-model="attendance" @updated="api.setAttendance(currentDateStr, attendance)" />
        </section>
        <section class="entries-section">
            <h2>Entries</h2>
            <DayEntryList :entries="thisDayEntries" @delete="deleteEntry" @edit="editEntry" />
        </section>
        <EditForm v-if="showEditForm" :entry="editingEntry" @save="saveEntry" @cancel="showEditForm = false" />
    </section>
</template>

<style scoped>
.timesheet-page {
    display: grid;
    gap: 1.5rem;
}

.timesheet-date {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.65rem;
    color: var(--text);
    font-size: 0.85rem;
}

.timesheet-date input {
    max-width: 100%;
}

.timesheet-focus {
    position: sticky;
    top: 3.5rem;
    z-index: 10;
    display: grid;
    justify-items: center;
    gap: 1.25rem;
    padding: 1.25rem 1.75rem;
    border: 1px solid var(--border);
    border-top: 3px solid var(--accent);
    border-radius: 0.5rem;
    background: var(--code-bg);
}

.primary-button {
    width: min(100%, 18rem);
    font-weight: 600;
}

.entries-section h2 {
    margin: 0 0 0.75rem;
    font-size: 1.3rem;
}

@media (max-width: 480px) {
    .timesheet-page {
        gap: 1rem;
        padding-top: 1rem;
    }

    .timesheet-date {
        justify-content: flex-start;
    }

    .timesheet-focus {
        gap: 0.9rem;
        padding: 1rem 0.75rem;
    }
}
</style>