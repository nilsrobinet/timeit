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
        // Extract the time portion from the ISO string
        // TODO: make this respect local time instead of always using UTC
        // TODO: make this more robust and less ugly
        return this.date.toISOString().split('T')[1].split('.')[0]
    }
}

export default TimeKeepingEntry