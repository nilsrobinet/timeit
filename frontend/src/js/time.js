/**
 * @module time
 * Utility functions and classes for handling time and date operations.
 */


/**
 * Get today's date in YYYY-MM-DD format.
 * @returns {string} The formatted date string for today.
 */
function formatToday() {
    const today = new Date().toISOString().split('T')[0]
    return today
}

/**
 * 
 * @param {Date} date1 
 * @param {Date} date2 
 * @returns {FDuration} The duration difference between the two dates.
 */
function getDateDurationDelta(date1, date2) {
    if (!(date1 instanceof Date)) {
        date1 = new Date(date1)
    }
    if (!(date2 instanceof Date)) {
        date2 = new Date(date2)
    }

    let secondsDelta = (date1.getTime() - date2.getTime()) / 1000

    return new FDuration(secondsDelta)
}

class FDuration {

    /**
     * @param {string|Object} duration - The duration as a string in the format "+HH:MM:SS" or "-HH:MM:SS", or an object with sign, hours, minutes, and seconds properties.
     */
    constructor(duration) {
        if (typeof duration === 'string') {
            const sign = duration.startsWith('-') ? '-' : '+'
            const [hours, minutes, seconds] = duration.replace(/^[-+]/, '').split(':').map(Number)
            this.duration = { sign, hours, minutes, seconds }
        } else if (typeof duration === 'number') {
            const sign = duration < 0 ? '-' : '+'
            const absSeconds = Math.abs(duration)
            const hours = Math.floor(absSeconds / 3600)
            const minutes = Math.floor((absSeconds % 3600) / 60)
            const seconds = Math.floor(absSeconds % 60)
            this.duration = { sign, hours, minutes, seconds }
        } else if (duration instanceof FDuration) {
            this.duration = duration.duration
        } else {
            throw new Error('Invalid duration format: ' + duration)
        }
    }

    /**
     * @returns {string} The formatted duration string in the format "+HH:MM:SS" or "-HH:MM:SS"
     */
    toString() {
        const {sign, hours, minutes, seconds } = this.duration
        return `${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }

    delta(duration) {
        const { sign: sign1, hours: hours1, minutes: minutes1, seconds: seconds1 } = this.duration
        const { sign: sign2, hours: hours2, minutes: minutes2, seconds: seconds2 } = duration.duration

        const totalSeconds1 = (sign1 === '-' ? -1 : 1) * (hours1 * 3600 + minutes1 * 60 + seconds1)
        const totalSeconds2 = (sign2 === '-' ? -1 : 1) * (hours2 * 3600 + minutes2 * 60 + seconds2)

        const deltaSeconds = totalSeconds1 - totalSeconds2
        const sign = deltaSeconds < 0 ? '-' : '+'
        const absSeconds = Math.abs(deltaSeconds)
        const hours = Math.floor(absSeconds / 3600)
        const minutes = Math.floor((absSeconds % 3600) / 60)
        const seconds = Math.floor(absSeconds % 60)

        return new FDuration(`${sign}${hours}:${minutes}:${seconds}`)
    }
}

class FDate {
    /**
     * @param {string|Date} date - The date as a string in the format "YYYY-MM-DD" or a Date object.
     */
    constructor(date) {
        if (date instanceof Date) {
            this.date = date
        } else {
            const [year, month, day] = date.split('-').map(Number)
            this.date = new Date(year, month - 1, day)
        }
    }

    /**
     * @returns {string} The formatted date string in the format "YYYY-MM-DD"
     */
    toString() {
        const year = this.date.getFullYear()
        const month = String(this.date.getMonth() + 1).padStart(2, '0')
        const day = String(this.date.getDate()).padStart(2, '0')
        return `${year}-${month}-${day}`
    }
}

export { FDuration, FDate, formatToday, getDateDurationDelta }