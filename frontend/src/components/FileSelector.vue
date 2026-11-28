<script setup>
import { ref } from 'vue'

const emit = defineEmits(['cancel', 'dropped'])
const file = ref(null)
</script>

<template>
    <div class="form-backdrop" @click.self="$emit('cancel')">
        <section class="form-dialog file-selector-dialog" role="dialog" aria-modal="true"
            aria-labelledby="file-selector-title">
            <header>
                <h2 id="file-selector-title">Import data</h2>
                <p>Select a JSON backup file to import.</p>
            </header>
            <label for="import-file">JSON file</label>
            <input id="import-file" class="form-control file-input" type="file"
                @change="file = $event.target.files[0] ?? null" accept=".json" />
            <div class="file-selector-actions">
                <button class="button button-accent" :disabled="!file"
                    @click="emit('dropped', file)">Import</button>
                <button class="button button-outline" @click="emit('cancel')">Cancel</button>
            </div>
        </section>
    </div>
</template>

<style scoped>
.file-selector-dialog {
    display: grid;
    gap: 1rem;
}

.file-selector-dialog header h2 {
    margin: 0;
}

.file-selector-dialog header p {
    margin: 0.35rem 0 0;
    color: var(--text);
}

.file-input {
    width: 100%;
    padding: 0.75rem;
    border-style: dashed;
    background: var(--code-bg);
}

.file-input::file-selector-button {
    margin-right: 0.75rem;
    padding: 0.45rem 0.65rem;
    border: 1px solid var(--border);
    border-radius: 0.25rem;
    background: var(--bg);
    color: var(--text-h);
    font: inherit;
    cursor: pointer;
}

.file-selector-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
}

.file-selector-actions button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
}

@media (max-width: 480px) {
    .file-selector-actions button {
        flex: 1;
    }
}
</style>
