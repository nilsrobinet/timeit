<template>
  <header class="app-header">
    <nav aria-label="Main navigation">
      <RouterLink class="navbar-item" exact-active-class="navbar-item-active" to="/">Timesheet</RouterLink>
      <RouterLink class="navbar-item" exact-active-class="navbar-item-active" to="/history">History</RouterLink>
      <RouterLink class="navbar-item" exact-active-class="navbar-item-active" to="/stats">Stats</RouterLink>
      <RouterLink class="navbar-item" exact-active-class="navbar-item-active" to="/settings">Settings</RouterLink>
    </nav>
  </header>
  <main>
    <RouterView />
  </main>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  height: 3.5rem;
  padding: 0.5rem 0.25rem;
  background-color: var(--bg);
  border-bottom: 1px solid var(--border);
  box-sizing: border-box;
}

.app-header nav {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap;
  width: 100%;
  gap: clamp(0.05rem, 0.8vw, 0.25rem);
}

.navbar-item {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 0;
  white-space: nowrap;
  padding: 0.45rem 0.1rem;
  color: var(--text);
  text-decoration: none;
  font-size: clamp(0.6rem, 3.5vw, 0.9rem);
  line-height: 1.3;
  transition:
    background-color 0.15s ease,
    color 0.15s ease;
}

@media (max-width: 240px) {
  .navbar-item {
    padding-inline: 0.05rem;
    font-size: 0.5rem;
  }
}

.navbar-item:hover {
  color: var(--text-h);
  background-color: var(--code-bg);
}

.navbar-item-active {
  color: var(--text-h);
  box-shadow: inset 0 -2px var(--accent);
}

.navbar-item:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
</style>