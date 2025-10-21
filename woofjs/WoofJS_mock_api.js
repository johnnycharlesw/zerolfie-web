class __WoofJS__IO_Stream {
    constructor(){
        this.text = '';
    }
    append(str) { this.text += str; }
    setText(str) { this.text = str; }
    getText() { return this.text; }
}

class __WoofJS__Mock_API {
    // Mock WoofJS API for testing purposes

    stdout = new __WoofJS__IO_Stream();

    stderr = new __WoofJS__IO_Stream();

    getCurrentUnixTimestamp(y2k38safe=true, inMilliseconds=true) {
        // Return current Unix timestamp in milliseconds
        let now = Date.now(); // milliseconds since epoch
        if (!inMilliseconds) {
            now = Math.floor(now / 1000); // convert to seconds
        }
        return now;
    }

    
}

export let __WoofJS__ = new __WoofJS__Mock_API();