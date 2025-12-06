// Intl is a namespace object, not a constructor
const Intl = {
    // Intl.Collator - for locale-aware string comparison
    Collator: class Collator {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
        }
        
        compare(x, y) {
            // Use String.prototype.localeCompare if available
            if (typeof x === 'string' && typeof y === 'string') {
                return x.localeCompare(y, this._locales, this._options);
            }
            // Fallback: simple string comparison
            return String(x) < String(y) ? -1 : String(x) > String(y) ? 1 : 0;
        }
        
        resolvedOptions() {
            return { ...this._options, locale: this._locales[0] || 'en' };
        }
        
        static supportedLocalesOf(locales, options) {
            // Simplified: return locales as-is (real implementation would check ICU support)
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.DateTimeFormat - for locale-aware date/time formatting
    DateTimeFormat: class DateTimeFormat {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
        }
        
        format(date) {
            // Use Date.prototype.toLocaleString if available
            if (date instanceof Date) {
                return date.toLocaleString(this._locales, this._options);
            }
            // Fallback: convert to string
            return String(date);
        }
        
        formatRange(start, end) {
            // Simplified: format both dates
            return `${this.format(start)} – ${this.format(end)}`;
        }
        
        formatRangeToParts(start, end) {
            // Simplified: return parts for both dates
            return [
                ...this.formatToParts(start),
                { type: 'literal', value: ' – ' },
                ...this.formatToParts(end)
            ];
        }
        
        formatToParts(date) {
            // Simplified: basic parts structure
            if (date instanceof Date) {
                return [
                    { type: 'year', value: String(date.getFullYear()) },
                    { type: 'month', value: String(date.getMonth() + 1) },
                    { type: 'day', value: String(date.getDate()) }
                ];
            }
            return [{ type: 'literal', value: String(date) }];
        }
        
        resolvedOptions() {
            return {
                ...this._options,
                locale: this._locales[0] || 'en',
                calendar: this._options.calendar || 'gregory',
                numberingSystem: this._options.numberingSystem || 'latn'
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.ListFormat - for locale-aware list formatting
    ListFormat: class ListFormat {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
            this._type = this._options.type || 'conjunction';
            this._style = this._options.style || 'long';
        }
        
        format(list) {
            if (!Array.isArray(list)) {
                throw new TypeError('ListFormat.format requires an array');
            }
            
            // Simplified formatting based on type
            const separator = this._type === 'disjunction' ? ' or ' : 
                            this._type === 'unit' ? ' ' : ', ';
            
            if (list.length === 0) return '';
            if (list.length === 1) return String(list[0]);
            if (list.length === 2) {
                return `${list[0]}${separator}${list[1]}`;
            }
            
            const last = list.pop();
            return `${list.join(', ')}${separator}${last}`;
        }
        
        formatToParts(list) {
            if (!Array.isArray(list)) {
                throw new TypeError('ListFormat.formatToParts requires an array');
            }
            
            const parts = [];
            for (let i = 0; i < list.length; i++) {
                parts.push({ type: 'element', value: String(list[i]) });
                if (i < list.length - 1) {
                    parts.push({ type: 'literal', value: ', ' });
                }
            }
            return parts;
        }
        
        resolvedOptions() {
            return {
                locale: this._locales[0] || 'en',
                type: this._type,
                style: this._style
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.NumberFormat - for locale-aware number formatting
    NumberFormat: class NumberFormat {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
        }
        
        format(number) {
            // Use Number.prototype.toLocaleString if available
            const num = Number(number);
            if (typeof num.toLocaleString === 'function') {
                return num.toLocaleString(this._locales, this._options);
            }
            // Fallback: basic formatting
            return num.toString();
        }
        
        formatRange(start, end) {
            return `${this.format(start)} – ${this.format(end)}`;
        }
        
        formatRangeToParts(start, end) {
            return [
                ...this.formatToParts(start),
                { type: 'literal', value: ' – ' },
                ...this.formatToParts(end)
            ];
        }
        
        formatToParts(number) {
            const num = Number(number);
            const str = this.format(num);
            // Simplified: return basic parts
            return [{ type: 'integer', value: str }];
        }
        
        resolvedOptions() {
            return {
                ...this._options,
                locale: this._locales[0] || 'en',
                numberingSystem: this._options.numberingSystem || 'latn'
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.PluralRules - for locale-aware plural rules
    PluralRules: class PluralRules {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
        }
        
        select(number) {
            // Simplified plural rules (real implementation would use ICU)
            const num = Number(number);
            if (num === 0) return 'zero';
            if (num === 1) return 'one';
            if (num === 2) return 'two';
            return 'other';
        }
        
        resolvedOptions() {
            return {
                locale: this._locales[0] || 'en',
                pluralCategories: ['zero', 'one', 'two', 'few', 'many', 'other'],
                type: this._options.type || 'cardinal'
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.RelativeTimeFormat - for locale-aware relative time formatting
    RelativeTimeFormat: class RelativeTimeFormat {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
            this._numeric = this._options.numeric || 'always';
            this._style = this._options.style || 'long';
        }
        
        format(value, unit) {
            // Simplified relative time formatting
            const num = Number(value);
            const units = {
                'second': num === 1 ? 'second' : 'seconds',
                'minute': num === 1 ? 'minute' : 'minutes',
                'hour': num === 1 ? 'hour' : 'hours',
                'day': num === 1 ? 'day' : 'days',
                'week': num === 1 ? 'week' : 'weeks',
                'month': num === 1 ? 'month' : 'months',
                'year': num === 1 ? 'year' : 'years'
            };
            const unitStr = units[unit] || unit;
            return `${num} ${unitStr} ago`;
        }
        
        formatToParts(value, unit) {
            const num = Number(value);
            return [
                { type: 'integer', value: String(num) },
                { type: 'literal', value: ' ' },
                { type: 'unit', value: unit }
            ];
        }
        
        resolvedOptions() {
            return {
                locale: this._locales[0] || 'en',
                style: this._style,
                numeric: this._numeric
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    // Intl.Segmenter - for locale-aware text segmentation
    Segmenter: class Segmenter {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
            this._granularity = this._options.granularity || 'grapheme';
        }
        
        segment(text) {
            // Simplified segmentation (real implementation would use ICU)
            const str = String(text);
            const segments = [];
            
            if (this._granularity === 'grapheme') {
                // Basic grapheme segmentation
                for (let i = 0; i < str.length; i++) {
                    segments.push({
                        segment: str[i],
                        index: i,
                        input: str,
                        isWordLike: /[a-zA-Z0-9]/.test(str[i])
                    });
                }
            } else {
                // Word/sentence segmentation would be more complex
                segments.push({
                    segment: str,
                    index: 0,
                    input: str,
                    isWordLike: true
                });
            }
            
            return {
                containing: (index) => {
                    for (const seg of segments) {
                        if (index >= seg.index && index < seg.index + seg.segment.length) {
                            return seg;
                        }
                    }
                    return null;
                },
                [Symbol.iterator]: function* () {
                    for (const seg of segments) {
                        yield seg;
                    }
                }
            };
        }
        
        resolvedOptions() {
            return {
                locale: this._locales[0] || 'en',
                granularity: this._granularity
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    
    // Intl.StringComparator - for locale-aware string comparison (proposal)
    StringComparator: class StringComparator {
        constructor(locales, options) {
            this._locales = locales || [];
            this._options = options || {};
        }
        
        compare(x, y) {
            if (typeof x === 'string' && typeof y === 'string') {
                return x.localeCompare(y, this._locales, this._options);
            }
            return String(x).localeCompare(String(y), this._locales, this._options);
        }
        
        resolvedOptions() {
            return {
                locale: this._locales[0] || 'en',
                ...this._options
            };
        }
        
        static supportedLocalesOf(locales, options) {
            return Array.isArray(locales) ? locales : [locales];
        }
    },
    
    // Static method: getCanonicalLocales
    getCanonicalLocales(locales) {
        const normalized = Array.isArray(locales) ? locales : [locales];
        return normalized.map(loc => String(loc).toLowerCase());
    }
};

// Expose Intl globally
globalThis.Intl = Intl;