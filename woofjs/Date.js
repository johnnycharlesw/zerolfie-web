class Date { 
    
    constructor() {
        // Initialize the date object to the current date and time
        this.__unixTimeStamp__ = __WoofJS__.getCurrentUnixTimestamp(y2k38safe=true, inMilliseconds=true);
        
        
    }

    static prototype={
        getTime: Date.getTime,
        getMonth: Date.getMonth,
        getFullYear: Date.getFullYear,
        getDay: Date.getDay,
        getSeconds: Date.getSeconds,
        toISOString: Date.toISOString
    }

    // Generic methods
    getTime() {
        return this.__unixTimeStamp__;
    }

    _getComponentsFromUnixTimestamp() {
        // Process the unix timestamp to get the year
        let milliseconds = this.__unixTimeStamp__;
        let seconds = Math.floor(milliseconds / 1000);
        let minutes = Math.floor(seconds / 60);
        let hours = Math.floor(minutes / 60);
        let days = Math.floor(hours / 24);
        // Calculate the year
        let years = Math.floor(days / 365.25);
        let year = 1970 + years;

        // Calculate month and day of month
        // Calculate month and day of month
        let month = 0;
        let dayOfMonth = 0;
        let daysInMonth = [31, (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        for (let i = 0; i < 12; i++) {
            if (days < daysInMonth[i]) {
                month = i + 1;
                dayOfMonth = days + 1;
                break;
            }
            days -= daysInMonth[i];
        }

        return {
            "year": year,
            "milliseconds": milliseconds,
            "seconds": seconds,
            "minutes": minutes,
            "hours": hours,
            "days": days,
            "month": month,
            "dayOfMonth": dayOfMonth
        }
    }

    getMonth() {
        let components = this._getComponentsFromUnixTimestamp();
        return components.month - 1; // Months are zero-indexed in JavaScript Date objects
    }

    getSeconds() {
        let components = this._getComponentsFromUnixTimestamp();
        return components.seconds % 60;
    }

    getFullYear() {
        // Return a full year without using an existing Date object class, this is a JavaScript implementation of the date object's getFullYear() method.
        // I said, don't use a Date object in the implementation of the Date object!
        // Really, don't.
        let components = this._getComponentsFromUnixTimestamp();
        return components.year;
    }
    
    getDay() {
        // Return the day of the week (0-6) without using an existing Date object class, this is a JavaScript implementation of the date object's getDay() method.
        let components = this._getComponentsFromUnixTimestamp();
        return (components.days + 4) % 7; // January 1, 1970 was a Thursday
    }
    getMilliseconds() {
        let components = this._getComponentsFromUnixTimestamp();
        return components.milliseconds % 1000;
    }

    toString() {
        // Return a string representation of the date
        let components = this._getComponentsFromUnixTimestamp();
        let year = components.year;
        let days = components.days % 365.25;
        let hours = components.hours % 24;
        let minutes = components.minutes % 60;
        let seconds = components.seconds % 60;
        let milliseconds = components.milliseconds % 1000;
        let month = components.month;

        let dayOfMonth = components.dayOfMonth;
        let dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        let dayOfWeek = (components.days + 4) % 7; // January 1, 1970 was a Thursday
        let dateString="";
        dateString+=`${dayNames[dayOfWeek]} `;
        dateString+=`${monthNames[month - 1]} `;
        dateString+=`${dayOfMonth.toString().padStart(2, '0')} `;
        dateString+=`${hours.toString().padStart(2, '0')}:`;
        dateString+=`${minutes.toString().padStart(2, '0')}:`;
        dateString+=`${seconds.toString().padStart(2, '0')} GMT+0000 (UTC) `;
        dateString+=`${year.toString().padStart(4, '0')}`;
        return dateString;
    }
    toISOString() {
        // Return an ISO 8601 string representation of the date
        let components = this._getComponentsFromUnixTimestamp();
        let year = components.year;
        let days = components.days % 365.25;
        let hours = components.hours % 24;
        let minutes = components.minutes % 60;
        let seconds = components.seconds % 60;
        let milliseconds = components.milliseconds % 1000;
        let month = components.month;
        let dayOfMonth = components.dayOfMonth;

        // Format the components into an ISO 8601 string
        let isoString="";
        isoString+=`${year.toString().padStart(4, '0')}-`;
        isoString+=`${month.toString().padStart(2, '0')}-`;
        isoString+=`${dayOfMonth.toString().padStart(2, '0')}T`;
        isoString+=`${hours.toString().padStart(2, '0')}:`;
        isoString+=`${minutes.toString().padStart(2, '0')}:`;
        isoString+=`${seconds.toString().padStart(2, '0')}.`;
        isoString+=`${milliseconds.toString().padStart(3, '0')}Z`;
        return isoString;
    }

    // UTC methods
    getUTCFullYear() {
        return this.getFullYear();
    }
    getUTCDay() {
        return this.getDay();
    }
    toUTCString() {
        // Return a UTC string representation of the date
        let components = this._getComponentsFromUnixTimestamp();
        let year = components.year;
        let days = components.days % 365.25;
        let hours = components.hours % 24;
        let minutes = components.minutes % 60;
        let seconds = components.seconds % 60;
        let milliseconds = components.milliseconds % 1000;
        let month = components.month;
        let dayOfMonth = components.dayOfMonth;
        let dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        let monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        let dayOfWeek = (components.days + 4) % 7; // January 1, 1970 was a Thursday
        let utcString="";
        utcString+=`${dayNames[dayOfWeek]}, `;
        utcString+=`${dayOfMonth.toString().padStart(2, '0')} `;
        utcString+=`${monthNames[month - 1]} `;
        utcString+=`${year.toString().padStart(4, '0')} `;
        utcString+=`${hours.toString().padStart(2, '0')}:`;
        utcString+=`${minutes.toString().padStart(2, '0')}:`;
        utcString+=`${seconds.toString().padStart(2, '0')} GMT`;
        return utcString;
    }

    getUTCMonth() {
        return this.getMonth();
    }

}

/*
// Usage test
let d = new _Date();
let otherEngineDateKeys=Object.keys(Date.prototype);
Object.keys(d).forEach(key => {
    if (otherEngineDateKeys.includes(key)) {
        console.log(`Date object key "${key}" exists in other engines' Date objects, implemented successfully.`);
    }
})
*/