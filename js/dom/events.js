"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
string;
type;
EventTarget ? target : ;
EventTarget ? srcElement : ; // legacy
EventTarget ? currentTarget : ;
sequence < EventTarget > composedPath();
const NONE = 0;
const CAPTURING_PHASE = 1;
const AT_TARGET = 2;
const BUBBLING_PHASE = 3;
eventPhase: int;
stopPropagation();
{
    return; // stop propogation later
}
;
stopImmediatePropagation();
{
    return; // stop propogation later
}
;
bubbles: boolean;
cancelable: boolean;
preventDefault();
{
    this.defaultPrevented = true;
}
;
defaultPrevented: boolean;
boolean;
composed;
[LegacyUnforgeable];
boolean;
isTrusted;
DOMHighResTimeStamp;
timeStamp;
undefined;
initEvent(string, type, optional, boolean, bubbles = false, optional, boolean, cancelable = false); // legacy
;
boolean;
bubbles = false;
boolean;
cancelable = false;
boolean;
composed = false;
;
class EventTarget {
}
undefined;
addEventListener(string, type, EventListener ? callback : , optional(AddEventListenerOptions, or, boolean), options = {});
undefined;
removeEventListener(string, type, EventListener ? callback : , optional(EventListenerOptions, or, boolean), options = {});
boolean;
dispatchEvent(Event, event);
;
callback;
undefined;
handleEvent(Event, event);
;
dictionary;
EventListenerOptions;
{
    boolean;
    capture = false;
}
;
EventListenerOptions;
{
    passive: boolean;
    boolean;
    once = false;
    AbortSignal;
    signal;
}
;
class AbortSignal {
}
EventTarget;
{
    [NewObject];
    AbortSignal;
    abort(reason, any);
    {
        return new AbortSignal(reason);
    }
    ;
    [Exposed = (Window, Worker), NewObject];
    AbortSignal;
    timeout([EnforceRange], milliseconds, bigint);
    [NewObject];
    AbortSignal;
    _any(sequence < AbortSignal > signals);
    aborted: boolean;
    reason: any;
    throwIfAborted();
    {
        if (this.aborted) {
            throw new Error("Thrown since it aborted!");
        }
    }
    ;
    attribute;
    EventHandler;
    onabort;
}
;
class UIEvent {
}
Event;
{
    constructor(string, type, optional, UIEventInit, eventInitDict = {});
    {
    }
    ;
    Window ? view : ;
    long;
    detail;
}
;
dictionary;
UIEventInit: EventInit;
{
    Window ? view = null : ;
    long;
    detail = 0;
}
;
class FocusEvent {
}
UIEvent;
{
    constructor(string, type, optional, FocusEventInit, eventInitDict = {});
    {
        super();
    }
    ;
    EventTarget ? relatedTarget : ;
}
;
class MouseEvent {
}
UIEvent;
{
    constructor(string, type, optional, MouseEventInit, eventInitDict = {});
    {
        super();
    }
    ;
    screenX: int;
    screenY: int;
    clientX: int;
    clientY: int;
    layerX: int;
    layerY: int;
    ctrlKey: boolean;
    shiftKey: boolean;
    altKey: boolean;
    metaKey: boolean;
    button: int;
    buttons: int;
    relatedTarget ?  : EventTarget;
    getModifierState(string, keyArg);
    boolean;
    {
    }
    ;
}
;
class WheelEvent {
}
MouseEvent;
{
    constructor(string, type, optional, WheelEventInit, eventInitDict = {});
    {
        super();
    }
    ;
    const DOM_DELTA_PIXEL = 0x00;
    const DOM_DELTA_LINE = 0x01;
    const DOM_DELTA_PAGE = 0x02;
    deltaX: int;
    deltaY: int;
    deltaZ: int;
    deltaMode: int;
}
;
class InputEvent {
}
UIEvent;
{
    constructor(string, type, optional, InputEventInit, eventInitDict = {});
    data ?  : string;
    isComposing: boolean;
    inputType: string;
}
;
dictionary;
InputEventInit: UIEventInit;
{
    data ?  : string = null;
    isComposing: boolean = false;
    inputType: string = "";
}
;
UIEvent;
{
    constructor(string, type, optional, KeyboardEventInit, eventInitDict = {});
    // KeyLocationCode
    const unsigned, long, DOM_KEY_LOCATION_STANDARD = 0x00;
    const unsigned, long, DOM_KEY_LOCATION_LEFT = 0x01;
    const unsigned, long, DOM_KEY_LOCATION_RIGHT = 0x02;
    const unsigned, long, DOM_KEY_LOCATION_NUMPAD = 0x03;
    attribute;
    string;
    key;
    attribute;
    string;
    code;
    attribute;
    unsigned;
    long;
    location;
    attribute;
    boolean;
    ctrlKey;
    attribute;
    boolean;
    shiftKey;
    attribute;
    boolean;
    altKey;
    attribute;
    boolean;
    metaKey;
    attribute;
    boolean;
    repeat;
    attribute;
    boolean;
    isComposing;
    boolean;
    getModifierState(string, keyArg);
}
;
class CompositionEvent {
}
UIEvent;
{
    constructor(string, type, optional, CompositionEventInit, eventInitDict = {});
    {
    }
    ;
    data: string;
}
;
dictionary;
CompositionEventInit: UIEventInit;
{
    string;
    data = "";
}
;
//# sourceMappingURL=events.js.map