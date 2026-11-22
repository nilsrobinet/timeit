<script setup>
import { ref } from "vue"
import { ApiInteractor } from "../js/ApiInteractor"
const status = ref("inoffice")
const entries = ref([])

const api = new ApiInteractor()

function checkIn() {
    const date = new Date().toISOString().split("T")[0]
    api.addAttendance(status.value, date)
    loadEntries()
}

function loadEntries() {
    api.getAttendance().then(data => entries.value = data)
}
loadEntries()

</script>

<template>
    <section class="content-page attendance-page">
        <h1>Attendance</h1>
        <div class="attendance-controls">
            <label for="attendance-status">Status</label>
            <select id="attendance-status" class="form-control" v-model="status">
                <option value="inoffice">In Office</option>
                <option value="remote">Remote</option>
                <option value="sick" disabled>Sick</option>
                <option value="vacation" disabled>Vacation</option>
            </select>
            <button class="button attendance-submit" @click="checkIn">Check In</button>
        </div>
        <ul class="attendance-list">
            <li v-for="(record, date) in entries.records" :key="date">
                <time :datetime="date">{{ date }}</time>
                <span>{{ record.status }}</span>
            </li>
        </ul>
    </section>
</template>

<style scoped>
.attendance-controls {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border);
}

.attendance-controls label {
    color: var(--text);
}

.attendance-controls select {
    min-width: 10rem;
}

.attendance-submit {
    margin-left: auto;
}

.attendance-list {
    margin: 1rem 0 0;
    padding: 0;
    list-style: none;
}

.attendance-list li {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.85rem 0.5rem;
    border-bottom: 1px solid var(--border);
}

.attendance-list time {
    color: var(--text-h);
    font-variant-numeric: tabular-nums;
}

.attendance-list li > span {
    color: var(--text);
}

@media (max-width: 480px) {
    .attendance-controls {
        flex-wrap: wrap;
    }

    .attendance-controls select {
        flex: 1;
    }

    .attendance-submit {
        width: 100%;
        margin-left: 0;
    }
}
</style>