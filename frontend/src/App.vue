<script setup>
</script>


<template>
  <header class="app-header">
    <nav aria-label="Main navigation">
      <RouterLink to="/">Timesheet</RouterLink>
      <RouterLink to="/history">History</RouterLink>
      <RouterLink to="/attendance">Attendance</RouterLink>
      <RouterLink to="/settings">Settings</RouterLink>
    </nav>
  </header>
  <main>
    <RouterView />
  </main>
</template>