<script setup>
import { ref } from 'vue'
import { FDuration, FDate, formatToday } from './js/time'
import { ApiInteractor } from './js/ApiInteractor'
import StatsOverview from './components/StatsOverview.vue'
import DayEntryList from './components/EntryList.vue'
import EditForm from './components/EditForm.vue'

let currentDateStr = formatToday()

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
function editEntry(entry) {
  console.log('Editing entry:', entry)
  showEditForm.value = true
  editingEntry.value = entry
}
function checkInOut() {
  let type = isStarted.value ? 'stop' : 'start'
  api.addEntry(currentDateStr, type).then(() => {
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

</script>

<template>
  <main>
    <StatsOverview :summary="summary" />
    <DayEntryList :entries="thisDayEntries" @delete="deleteEntry" @edit="editEntry" />
    <button @click="checkInOut">{{ isStarted ? 'Check Out' : 'Check In' }}</button>
  </main>

  <div v-if="showEditForm" class="form-backdrop edit-form-backdrop" @click.self="showEditForm = false">
    <section class="form-dialog" role="dialog" aria-modal="true" aria-label="Edit Entry">
      <EditForm :entry="editingEntry" @save="saveEntry" />
    </section>
  </div>

</template>

<style>
.form-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  background: rgb(0 0 0 / 50%);
}

.form-dialog {
  padding: 1.5rem;
  background: white;
}
</style>