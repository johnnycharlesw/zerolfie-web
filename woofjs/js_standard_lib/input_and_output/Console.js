
class Console{
    constructor(){
        this._timers = {};
        this._counters = {};
        this._groupLevel = 0;
        this._prefix = '';
    }
    
    log(...args) {
        __WoofJS__.stdout.append(args.join(' ') + '\n');
    }

    error(...args) {
        __WoofJS__.stderr.append(args.join(' ') + '\n');
    }

    warn(...args) {
        __WoofJS__.stderr.append('Warning: ' + args.join(' ') + '\n');
    }
    

    assert(condition, ...args) {
        if (!condition) {
            this.error('Assertion failed:', ...args);
        }
    }

    clear () {
        __WoofJS__.stdout.setText('');
        __WoofJS__.stderr.setText('');
    }

    dir(obj) {
        this.log(JSON.stringify(obj, null, 2));
    }

    dirxml(obj) {
        this.dir(obj);
    }

    table(obj) {
        if (Array.isArray(obj)) {
            if (obj.length === 0) {
                this.log('[]');
                return;
            }
            const headers = Object.keys(obj[0]);
            const rows = obj.map(item => headers.map(header => item[header]));
            const table = [headers, ...rows];
            const colWidths = headers.map((header, i) => Math.max(...table.map(row => String(row[i]).length)));
            const separator = colWidths.map(width => '-'.repeat(width)).join(' | ');
            this.log(table.map(row => row.map((cell, i) => String(cell).padEnd(colWidths[i])).join(' | ')).join('\n'));
            this.log(separator);
        } else if (typeof obj === 'object' && obj !== null) {
            const entries = Object.entries(obj);
            const colWidths = [
                Math.max(...entries.map(([key]) => key.length), 'Key'.length),
                Math.max(...entries.map(([, value]) => String(value).length), 'Value'.length)
            ];
            const separator = colWidths.map(width => '-'.repeat(width)).join(' | ');
            this.log(['Key'.padEnd(colWidths[0]) + ' | ' + 'Value'.padEnd(colWidths[1]), separator, ...entries.map(([key, value]) => key.padEnd(colWidths[0]) + ' | ' + String(value).padEnd(colWidths[1]))].join('\n'));
        } else {
            this.error('Not an array or object');
        }
    }

    time(label = 'default') {
        if (!this._timers) {
            this._timers = {};
        }
        this._timers[label] = performance.now();
    }

    timeEnd(label = 'default') {
        if (this._timers && this._timers[label]) {
            const duration = performance.now() - this._timers[label];
            this.log(`${label}: ${duration.toFixed(3)}ms`);
            delete this._timers[label];
        } else {
            this.error(`No such label: ${label}`);
        }
    }
    trace() {
        const err = new Error();
        this.log(err.stack);
    }

    count(label = 'default') {
        if (!this._counters) {
            this._counters = {};
        }
        if (!this._counters[label]) {
            this._counters[label] = 0;
        }
        this._counters[label]++;
        this.log(`${label}: ${this._counters[label]}`);
    }
    countReset(label = 'default') {
        if (this._counters && this._counters[label]) {
            this._counters[label] = 0;
        } else {
            this.error(`No such label: ${label}`);
        }
    }

    group(label = '') {
        this.log(label);
        if (!this._groupLevel) {
            this._groupLevel = 0;
        }
        this._groupLevel++;
        this._updatePrefix();
    }
    groupEnd() {
        if (this._groupLevel && this._groupLevel > 0) {
            this._groupLevel--;
            this._updatePrefix();
        }
    }
    groupCollapsed(label = '') {
        this.group(label);
    }

    
}

export const console = new Console();
