import {FDuration, FDate, formatToday, formatDate} from './time'
import TimeKeepingEntry from './TimeKeepingEntry'

class ApiInteractor {
    buildUrl(path, params = {}) {
        const query = new URLSearchParams(params).toString()
        return `/api/${path}${query ? `?${query}` : ''}`
    }

    async getDay() {
        const day = await fetch(this.buildUrl('day')).then(r => r.json())
        return day
    }

    async getDays(from, limit = 10) {
        const days = await fetch(this.buildUrl('days', { from, limit })).then(r => r.json())
        return days
    }

    async getDaysSummary(from, limit = 10) {
        const summary = await fetch(this.buildUrl('days/summary', { from, limit })).then(r => r.json())
        return summary
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
        const avg_attendance = summary.avg_attendance
        return { dateObj, worked, target, day, weekly, total, lastEntry, avg_attendance }
    }

    /**
     * Delete an entry by its ID from the backend API
     * @param {Number} id 
     */
    async deleteEntry(id, date) {
         await fetch(this.buildUrl(`day`, { id: id, date: date}), {
            method: 'DELETE'
        })
    }

    /**
     * Add a new entry to the backend API
     * @param {TimeKeepingEntry} entry 
     */
    async addEntry(date, start) {
         await fetch(this.buildUrl('day/entry'), {
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
        await fetch(this.buildUrl(`day`, {id: entry.id}), {
           method: 'PATCH',
           headers: {
               'Content-Type': 'application/json'
           },
           body: JSON.stringify({ 'timestamp': entry.date, 'type': entry.type, date: formatDate(entry.date) })
        })
    }

    async setAttendance(date, status) {
        await fetch(this.buildUrl('day/attendance'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date: formatDate(date), status })
        })
    }

    async getConfig() {
        const config = await fetch(this.buildUrl('config'))
            .then(response => response.json()).then(data => data)
        return config
    }

    async postConfig(data) {
        await fetch(this.buildUrl('config'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
    }

    async getErrorList() {
        return fetch(this.buildUrl('report')).then(r => r.json())
    }

    async getAverageAttendance() {
        return fetch(this.buildUrl('days/attendance/avg')).then(r => r.json())
    }

    async getData() {
        return fetch(this.buildUrl('data')).then(r => r.json())
    }

    async postData(data) {
        await fetch(this.buildUrl('data'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
    }
}

export { ApiInteractor }