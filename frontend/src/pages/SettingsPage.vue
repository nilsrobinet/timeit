<script setup>
import { ref } from 'vue'
import { ApiInteractor } from '../js/ApiInteractor'
import FileSelector from '../components/FileSelector.vue'
import TimePicker from '../components/TimePicker.vue'

const api = new ApiInteractor()
const config = ref(null)
const showSelector = ref(false)
const days = ref({ 'MON': false, 'TUE': false, 'WED': false, 'THU': false, 'FRI': false, 'SAT': false, 'SUN': false })
const userwritable = ref(false)

function update() {
    api.getConfig().then(conf => {
        config.value = conf
        userwritable.value = conf.userwritable
        updateDaysFromConf()
    })
}

function exportData() {
    api.getData().then(data => {
        var a = document.createElement('a')
        a.href = URL.createObjectURL(new Blob([JSON.stringify(data)]))
        a.download = 'data.json'
        a.click()
    })
}

function importData(file) {
    const reader = new FileReader()
    reader.onload = e => {
        const data = JSON.parse(e.target.result)
        api.postData(data)
    }
    reader.readAsText(file)
    showSelector.value = false
}

function postConfig() {
    if (!config.value) return
    api.postConfig(config.value).then(() => update())
}

function updateConfFromDays() {
    let selected = []
    for (let d in days.value) {
        if (days.value[d]) selected.push(d)
    }
    config.value.attendance.workdays = selected
}

function updateDaysFromConf() {
    for (let d in days.value) {
        days.value[d] = config.value.attendance.workdays.includes(d)
    }
}

update()

</script>

<template>
    <section class="content-page settings-page">
        <h1>Settings</h1>
        <p v-if="!userwritable" id="userwritable-info">Settings are read-only</p>
        <form v-if="config" class="settings-form">
            <div class="settings-field">
                <label for="daily-target">Daily target</label>
                <!-- <input id="daily-target" class="form-control" type="text" placeholder="08:00" required
                    pattern="[0-9]{1,3}:[0-5][0-9]" title="Enter hours and minutes, e.g. 08:00"
                    v-model="config.work.target" /> -->
                <TimePicker id="daily-target" class="form-control" v-model="config.work.target" :show-seconds="false"
                    :disabled="!userwritable" />
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
                <input id="timekeeping-path" class="form-control" type="text" v-model="config.data.timekeeping_path"
                    :disabled="!userwritable" />
            </div>
            <div class="settings-field">
                <label for="attendance-target">Attendance target</label>
                <input id="attendance-target" class="form-control" type="number" v-model="config.attendance.target"
                    min="0" max="7" step="0.01" :disabled="!userwritable" />
            </div>
            <div class="settings-field">
                <label for="workdays">Workdays</label>
                <div class="workdays">
                    <label class="workday-option" for="workdays_mon">
                        <input id="workdays_mon" type="checkbox" v-model="days.MON" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Mon</span>
                    </label>
                    <label class="workday-option" for="workdays_tue">
                        <input id="workdays_tue" type="checkbox" v-model="days.TUE" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Tue</span>
                    </label>
                    <label class="workday-option" for="workdays_wed">
                        <input id="workdays_wed" type="checkbox" v-model="days.WED" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Wed</span>
                    </label>
                    <label class="workday-option" for="workdays_thu">
                        <input id="workdays_thu" type="checkbox" v-model="days.THU" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Thu</span>
                    </label>
                    <label class="workday-option" for="workdays_fri">
                        <input id="workdays_fri" type="checkbox" v-model="days.FRI" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Fri</span>
                    </label>
                    <label class="workday-option" for="workdays_sat">
                        <input id="workdays_sat" type="checkbox" v-model="days.SAT" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Sat</span>
                    </label>
                    <label class="workday-option" for="workdays_sun">
                        <input id="workdays_sun" type="checkbox" v-model="days.SUN" @change="updateConfFromDays"
                            :disabled="!userwritable" />
                        <span>Sun</span>
                    </label>
                </div>
            </div>
            <button class="button" type="submit" @click="postConfig" :disabled="!userwritable">Save</button>
        </form>
        <button class="button button-quiet" @click="exportData">Export Data</button>
        <button class="button button-quiet" @click="showSelector = true" :disabled="!userwritable">Import Data</button>
        <FileSelector v-if="showSelector" @cancel="showSelector = false" @dropped="importData" />
    </section>
</template>

<style scoped>
#userwritable-info {
    color: red;
}

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

.workdays {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem 1.25rem;
}

.workday-option {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    color: var(--text-h);
    cursor: pointer;
}

.workday-option input {
    flex: none;
    width: 1rem;
    height: 1rem;
    margin: 0;
    accent-color: var(--accent);
}

@media (max-width: 560px) {
    .settings-field {
        grid-template-columns: 1fr;
        gap: 0.4rem;
    }

    .workdays {
        display: grid;
        grid-template-columns: repeat(4, max-content);
        gap: 0.75rem 1.25rem;
    }
}
</style>