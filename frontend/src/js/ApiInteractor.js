import {FDuration, FDate, formatToday, formatDate} from './time'
import TimeKeepingEntry from './TimeKeepingEntry'

class ApiInteractor {
    buildUrl(path, params = {}) {
        const query = new URLSearchParams(params).toString()
        return `/api/${path}${query ? `?${query}` : ''}`
    }

    /**
     * Get a summary for the current day from the backend API
     * @returns {Object} An object containing the summary for the current day, including date, worked, target, day, weekly, and total durations
     */
    async getSummary(date = formatToday()) {
         const summary = await fetch(this.buildUrl('summary', { date }))
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
        const day = worked.delta(target)
        const lastEntry = summary.last_entry ? new TimeKeepingEntry(summary.last_entry) : null
        return { dateObj, worked, target, day, weekly, total, lastEntry }
    }

    /**
     * Get all entries for a specific day from the backend API
     * @param {String} date - The date in YYYY-MM-DD format
     * @returns {TimeKeepingEntry[]} An array of TimeKeepingEntry objects for the specified date
     */
    async getEntries(date = formatToday()) {
         const entries = await fetch(this.buildUrl('entries', { date }))
            .then(response => response.json()).then(data => data.entries)
        return entries.map(entry => new TimeKeepingEntry(entry)).sort((a, b) => a.date - b.date)
    }

    /**
     * Delete an entry by its ID from the backend API
     * @param {Number} id 
     */
    async deleteEntry(id) {
         await fetch(this.buildUrl(`entries/${encodeURIComponent(id)}`), {
            method: 'DELETE'
        })
    }

    /**
     * Add a new entry to the backend API
     * @param {TimeKeepingEntry} entry 
     */
    async addEntry(date, start) {
         await fetch(this.buildUrl('entries'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'date': date, 'type': start })
        })
    }

    /**
     * Edit an existing entry in the backend API
     * @param {TimeKeepingEntry} entry 
     */
    async editEntry(entry) {
        await fetch(this.buildUrl(`entries/${encodeURIComponent(entry.id)}`), {
           method: 'PATCH',
           headers: {
               'Content-Type': 'application/json'
           },
           body: JSON.stringify({ 'timestamp': entry.date, 'type': entry.type, date: formatDate(entry.date) })
        })
    }
}

export { ApiInteractor }