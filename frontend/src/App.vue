<script setup>
import { ref } from 'vue'
import { FDuration, FDate, formatToday } from './js/time'
import { ApiInteractor } from './js/ApiInteractor'
import StatsOverview from './components/StatsOverview.vue'
import DayEntryList from './components/EntryList.vue'
import EditForm from './components/EditForm.vue'

const currentDateStr = ref(formatToday())

const api = new ApiInteractor()

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
  api.getSummary(currentDateStr.value).then(data => {
    summary.value = data
    isStarted.value = data.lastEntry?.type === 'start'
  })
}
refreshSummary()

const thisDayEntries = ref([])
function refreshEntries() {
  api.getEntries(currentDateStr.value).then(data => {
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
function editEntry(entry) {
  console.log('Editing entry:', entry)
  showEditForm.value = true
  editingEntry.value = entry
}
function checkInOut() {
  let type = isStarted.value ? 'stop' : 'start'
  api.addEntry(currentDateStr.value, type).then(() => {
    refreshSummary()
    refreshEntries()
  })
}

const showEditForm = ref(false)
const editingEntry = ref(null)

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

</script>

<template>
  <main>
    <input v-model="currentDateStr" type="date" @change="onDateChange" />
    <StatsOverview :summary="summary" :do-live-update="currentDateStr == formatToday()" />
    <DayEntryList :entries="thisDayEntries" @delete="deleteEntry" @edit="editEntry" />
    <button @click="checkInOut">{{ getButtonText() }}</button>
  </main>

  <EditForm v-if="showEditForm" :entry="editingEntry" @save="saveEntry" @cancel="showEditForm = false" />

</template>