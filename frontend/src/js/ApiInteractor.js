import {FDuration, FDate, formatToday} from './time'
import TimeKeepingEntry from './TimeKeepingEntry'

class ApiInteractor {
    constructor(baseUrl) {
        this.baseUrl = baseUrl
    }

    /**
     * Get a summary for the current day from the backend API
     * @returns {Object} An object containing the summary for the current day, including date, worked, target, day, weekly, and total durations
     */
    async getSummary(date = formatToday()) {
        const summary = await fetch(`${this.baseUrl}/summary?date=${date}`)
            .then(response => response.json())
        const dateObj = new FDate(summary.date)
        const worked = new FDuration(summary.worked)
        const target = new FDuration(summary.target)
        if (summary.weekly_delta === undefined) {
            summary.weekly_delta = '+0:00:00'
        }
        const weekly = new FDuration(summary.weekly_delta)
        if (summary.total_delta === undefined) {
            summary.total_delta = '+0:00:00'
        }
        const total = new FDuration(summary.total_delta)
        const day = target.delta(worked)
        const lastEntry = summary.last_entry ? new TimeKeepingEntry(summary.last_entry) : null
        return { dateObj, worked, target, day, weekly, total, lastEntry }
    }

    /**
     * Get all entries for a specific day from the backend API
     * @param {String} date - The date in YYYY-MM-DD format
     */
    async getEntries(date = formatToday()) {
        const entries = await fetch(`${this.baseUrl}/entries?date=${date}`)
            .then(response => response.json()).then(data => data.entries)
        return entries.map(entry => new TimeKeepingEntry(entry))
    }

    /**
     * Delete an entry by its ID from the backend API
     * @param {Number} id 
     */
    async deleteEntry(id) {
        await fetch(`${this.baseUrl}/entries/${id}`, {
            method: 'DELETE'
        })
    }

    /**
     * Add a new entry to the backend API
     * @param {TimeKeepingEntry} entry 
     */
    async addEntry(date, start) {
        await fetch(`${this.baseUrl}/entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'date': date, 'type': start })
        })
    }
}

export { ApiInteractor }