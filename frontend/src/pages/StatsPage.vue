<script setup>
import { onMounted, ref } from 'vue'
import { ApiInteractor } from '../js/ApiInteractor'

const errors = ref([])
const loading = ref(true)
const loadFailed = ref(false)
const dismissed = ref(false)

const api = new ApiInteractor()

onMounted(async () => {
    try {
        errors.value = await api.getErrorList()
    } catch (error) {
        console.error('Failed to load the error report', error)
        loadFailed.value = true
    } finally {
        loading.value = false
    }
})
</script>

<template>
    <section class="content-page error-page">
        <section v-if="!dismissed" class="error-panel" aria-label="Data issues">
            <header class="error-heading">
                <h2>Data issues</h2>
                <span v-if="!loading && !loadFailed" class="error-count">
                    {{ errors.length }} {{ errors.length === 1 ? 'issue' : 'issues' }}
                </span>
                <button
                    v-if="errors.length > 0 || loadFailed"
                    class="button button-quiet error-dismiss"
                    type="button"
                    @click="dismissed = true"
                >
                    Dismiss
                </button>
            </header>
            <p v-if="loading" class="error-state" role="status">Checking for issues...</p>
            <p v-else-if="loadFailed" class="error-state error-state-failed" role="alert">
                Could not load the error report.
            </p>
            <p v-else-if="errors.length === 0" class="error-state" role="status">No issues found.</p>
            <ul v-else class="error-list" aria-label="Data issues">
                <li v-for="e in errors" :key="e">{{ e }}</li>
            </ul>
        </section>
    </section>
</template>

<style scoped>
.error-panel {
    max-width: 46rem;
}

.error-heading {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.75rem;
}

.error-heading h2 {
    margin: 0;
    font-size: 1.1rem;
}

.error-count {
    color: var(--danger);
    font-size: 0.9rem;
    font-weight: 500;
    white-space: nowrap;
}

.error-dismiss {
    margin-left: auto;
}

.error-list {
    display: grid;
    gap: 0.4rem;
    margin: 0;
    padding: 0;
    list-style: none;
    max-height: min(35vh, 16rem);
    overflow-y: auto;
    overscroll-behavior: contain;
}

.error-list li {
    min-width: 0;
    padding: 0.7rem 0.85rem;
    border: 1px solid var(--border);
    border-left: 4px solid var(--danger);
    border-radius: 0.3rem;
    background: var(--danger-bg);
    color: var(--text-h);
    overflow-wrap: anywhere;
}

.error-state {
    margin: 0;
    padding: 1rem;
    border-left: 3px solid var(--border);
    background: var(--code-bg);
    color: var(--text);
}

.error-state-failed {
    border-color: var(--danger);
    background: var(--danger-bg);
    color: var(--danger);
}

@media (max-width: 480px) {
    .error-heading {
        gap: 0.5rem;
    }

    .error-list li {
        padding: 0.65rem 0.75rem;
    }
}
</style>