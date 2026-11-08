class TimeKeepingEntry {
    constructor(entry) {
        this.type = entry.type
        this.date = new Date(entry.timestamp)
        this.id = entry.id
    }

    toString() {
        return `${this.type} - ${this.date.toISOString()}`
    }

    getTime() {
        const pad = value => String(value).padStart(2, '0')
        return `${pad(this.date.getHours())}:${pad(this.date.getMinutes())}:${pad(this.date.getSeconds())}`
    }
}

export default TimeKeepingEntry