<script setup>
import { ref } from 'vue'

const username = ref('')
const dailyTarget = ref('08:00')

</script>

<template>
    <div>
        <h1>Settings</h1>
        <form>
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" v-model="username">
            <label for="daily-target">Daily Target:</label>
            <input id="daily-target" type="text" placeholder="08:00" required pattern="[0-9]{1,3}:[0-5][0-9]"
                title="Enter hours and minutes, e.g. 08:00" v-model="dailyTarget" />
            <button type="submit">Save</button>
        </form>
    </div>
</template>