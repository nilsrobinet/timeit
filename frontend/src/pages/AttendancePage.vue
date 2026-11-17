<script setup>
import { ref } from "vue"
import { ApiInteractor } from "../js/ApiInteractor"
const status = ref("inoffice")
const entries = ref([])

const api = new ApiInteractor()

function checkIn() {
    console.log(status.value)
    const date = new Date().toISOString().split("T")[0]
    console.log(date)
    api.addAttendance(status.value, date)
    loadEntries()
}

function loadEntries() {
    api.getAttendance().then(data => entries.value = data)
}
loadEntries()

</script>

<template>
    <div>
        <h1>Attendance</h1>
        <button @click="checkIn">Check In</button>
        <select v-model="status">
            <option value="inoffice">In Office</option>
            <option value="remote">Remote</option>
            <option value="sick" disabled>Sick</option>
            <option value="vacation" disabled>Vacation</option>
        </select>
    </div>
    <ul>
        <li v-for="(record, date) in entries.records" :key="date">
            {{ date }} - {{ record.status }}
        </li>
    </ul>
</template>