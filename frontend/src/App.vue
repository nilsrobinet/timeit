<script setup>
import { ref } from 'vue'
import { FDuration, FDate, formatToday } from './js/time'
import { ApiInteractor } from './js/ApiInteractor'
import CurrentTimer from './components/StatsOverview.vue'
import DayEntryList from './components/DayEntryList.vue'

let currentDateStr = formatToday()

const api = new ApiInteractor('http://localhost:8080/api')

const summary = ref({
  date: new FDate(new Date()),
  worked: new FDuration('+0:00:00'),
  target: new FDuration('+8:00:00'),
  day: new FDuration('+0:00:00'),
  weekly: new FDuration('+0:00:00'),
  total: new FDuration('+0:00:00')
})
const isStarted = ref(false)
function refreshSummary() {
  api.getSummary(currentDateStr).then(data => {
    summary.value = data
    isStarted.value = data.lastEntry?.type === 'start'
  })
}
refreshSummary()

const thisDayEntries = ref([])
function refreshEntries() {
  api.getEntries(currentDateStr).then(data => {
    thisDayEntries.value = data
  })
}
refreshEntries()

function deleteEntry(id) {
  api.deleteEntry(id).then(() => {
    thisDayEntries.value = thisDayEntries.value.filter(entry => entry.id !== id)
    refreshSummary()
  })
}
function editEntry(id) {
  console.log('Edit', id)
}
function checkInOut() {
  let type = isStarted.value ? 'stop' : 'start'
  api.addEntry(currentDateStr, type).then(() => {
    refreshSummary()
    refreshEntries()
  })
}

</script>

<template>
  <CurrentTimer :summary="summary" />
  <DayEntryList :entries="thisDayEntries" @delete="deleteEntry" @edit="editEntry" />
  <button @click="checkInOut">{{ isStarted ? 'Check Out' : 'Check In' }}</button>
</template>
