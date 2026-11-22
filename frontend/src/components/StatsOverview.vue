<script setup>
import { onUnmounted, ref } from 'vue'
import { FDuration, getDateDurationDelta } from '../js/time.js'

const props = defineProps({
    summary: Object,
    doLiveUpdate: Boolean
})

const currentWorked = ref(new FDuration(props.summary.worked))

function updateCurrentWorked(newWorked) {
    if (props.summary.lastEntry?.type === 'start' && props.doLiveUpdate) {
        const deltaAdder = getDateDurationDelta(new Date(props.summary.lastEntry.date), new Date())
        currentWorked.value = props.summary.worked.delta(deltaAdder)
    } else {
        currentWorked.value = props.summary.worked
    }
}
const intervalId = setInterval(() => {
    updateCurrentWorked(props.summary.worked)
}, 100)

onUnmounted(() => clearInterval(intervalId))

updateCurrentWorked(props.summary.worked)

</script>

<template>
    <section class="stats-overview" aria-label="Time summary">
        <div class="primary-stat">
            <h2><span id="worked">{{ currentWorked.toString(true) }}</span></h2>
            <p class="target-line"> / <strong id="target">{{ summary.target.toString(true) }}</strong></p>
        </div>
        <div class="stats-details">
            <div id="day" class="stat-item">
                <span>Daily balance</span>
                <strong>{{ summary.day.toString() }}</strong>
            </div>
            <div id="weekly" class="stat-item">
                <span>Weekly balance</span>
                <strong>{{ summary.weekly.toString() }}</strong>
            </div>
            <div id="total" class="stat-item">
                <span>Total balance</span>
                <strong>{{ summary.total.toString() }}</strong>
            </div>
        </div>
    </section>
</template>

<style scoped>
.stats-overview {
    width: 100%;
}

.primary-stat {
    text-align: center;
}

.primary-stat h2 {
    margin: 0.35rem 0 0;
    color: var(--text-h);
    font-size: clamp(2.5rem, 8vw, 4rem);
    font-weight: 600;
    line-height: 1.05;
    letter-spacing: -0.04em;
    font-variant-numeric: tabular-nums;
}

.target-line {
    margin-top: 0.35rem;
    color: var(--text);
    font-size: 0.95rem;
}

.target-line strong {
    color: var(--text-h);
    font-weight: 500;
    font-variant-numeric: tabular-nums;
}

.stats-details {
    display: flex;
    justify-content: space-around;
    gap: 1rem;
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
}

.stat-item {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    color: var(--text);
    font-size: 0.85rem;
}

.stat-item strong {
    color: var(--text-h);
    font-size: 1.05rem;
    font-variant-numeric: tabular-nums;
}

@media (max-width: 420px) {
    .stats-details {
        justify-content: space-between;
        gap: 0.5rem;
    }

    .stat-item {
        font-size: 0.7rem;
    }

    .stat-item strong {
        font-size: 0.85rem;
    }
}
</style>