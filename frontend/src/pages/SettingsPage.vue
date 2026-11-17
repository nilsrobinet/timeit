<script setup>
import { ref } from 'vue'
import { ApiInteractor } from '../js/ApiInteractor'

const config = ref(null)

const api = new ApiInteractor()
api.getConfig().then(conf => {
    config.value = conf

    config.value.work.target = config.value.work.target.join(":")
})

</script>

<template>
    <div>
        <h1>Settings</h1>
        <form v-if="config">
            <label for="daily-target">Daily Target:</label>
            <input id="daily-target" type="text" placeholder="08:00" required pattern="[0-9]{1,3}:[0-5][0-9]"
                title="Enter hours and minutes, e.g. 08:00" v-model="config.work.target" disabled />
            <br />
            <label for="persistance">Persistence method:</label>
            <select v-model="config.data.persistence" id="persistance" disabled>
                <option value="json">JSON</option>
                <option value="sqlite">SQLite</option>
            </select>
            <br />
            <label for="timekeeping-path">Timekeeping path:</label>
            <input id="timekeeping-path" type="text" v-model="config.data.timekeeping_path" disabled />
            <br />
            <label for="attendance-path">Attendance path:</label>
            <input id="attendance-path" type="text" v-model="config.data.attendance_path" disabled />
            <br />

            <button type="submit">Save</button>
        </form>
    </div>
</template>