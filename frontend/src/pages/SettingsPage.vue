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
    <section class="content-page settings-page">
        <h1>Settings</h1>
        <form v-if="config" class="settings-form">
            <div class="settings-field">
                <label for="daily-target">Daily target</label>
                <input id="daily-target" class="form-control" type="text" placeholder="08:00" required pattern="[0-9]{1,3}:[0-5][0-9]"
                    title="Enter hours and minutes, e.g. 08:00" v-model="config.work.target" disabled />
            </div>
            <div class="settings-field">
                <label for="persistance">Persistence method</label>
                <select class="form-control" v-model="config.data.persistence" id="persistance" disabled>
                    <option value="json">JSON</option>
                    <option value="sqlite">SQLite</option>
                </select>
            </div>
            <div class="settings-field">
                <label for="timekeeping-path">Timekeeping path</label>
                <input id="timekeeping-path" class="form-control" type="text" v-model="config.data.timekeeping_path" disabled />
            </div>
            <div class="settings-field">
                <label for="attendance-path">Attendance path</label>
                <input id="attendance-path" class="form-control" type="text" v-model="config.data.attendance_path" disabled />
            </div>

            <button class="button" type="submit">Save</button>
        </form>
    </section>
</template>

<style scoped>
.settings-form {
    display: grid;
    gap: 1rem;
    max-width: 42rem;
}

.settings-field {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) minmax(0, 2fr);
    align-items: center;
    gap: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}

.settings-field label {
    color: var(--text-h);
}

.settings-field input,
.settings-field select {
    width: 100%;
    min-width: 0;
}

.settings-form button {
    justify-self: start;
}

@media (max-width: 560px) {
    .settings-field {
        grid-template-columns: 1fr;
        gap: 0.4rem;
    }
}
</style>