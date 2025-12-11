"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
DOMString;
type;
EventTarget ? target : ;
EventTarget ? srcElement : ; // legacy
EventTarget ? currentTarget : ;
sequence < EventTarget > composedPath();
const unsigned, short, NONE = 0;
const unsigned, short, CAPTURING_PHASE = 1;
const unsigned, short, AT_TARGET = 2;
const unsigned, short, BUBBLING_PHASE = 3;
unsigned;
short;
eventPhase;
undefined;
stopPropagation();
attribute;
boolean;
cancelBubble; // legacy alias of .stopPropagation()
undefined;
stopImmediatePropagation();
boolean;
bubbles;
boolean;
cancelable;
attribute;
boolean;
returnValue; // legacy
undefined;
preventDefault();
boolean;
defaultPrevented;
boolean;
composed;
[LegacyUnforgeable];
boolean;
isTrusted;
DOMHighResTimeStamp;
timeStamp;
undefined;
initEvent(DOMString, type, optional, boolean, bubbles = false, optional, boolean, cancelable = false); // legacy
;
dictionary;
EventInit;
{
    boolean;
    bubbles = false;
    boolean;
    cancelable = false;
    boolean;
    composed = false;
}
;
undefined;
addEventListener(DOMString, type, EventListener ? callback : , optional(AddEventListenerOptions, or, boolean), options = {});
undefined;
removeEventListener(DOMString, type, EventListener ? callback : , optional(EventListenerOptions, or, boolean), options = {});
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
dictionary;
AddEventListenerOptions: EventListenerOptions;
{
    boolean;
    passive;
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
    timeout([EnforceRange], unsigned, long, long, milliseconds);
    [NewObject];
    AbortSignal;
    _any(sequence < AbortSignal > signals);
    boolean;
    aborted;
    any;
    reason;
    undefined;
    throwIfAborted();
    attribute;
    EventHandler;
    onabort;
}
;
class UIEvent {
}
Event;
{
    constructor(DOMString, type, optional, UIEventInit, eventInitDict = {});
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
    constructor(DOMString, type, optional, FocusEventInit, eventInitDict = {});
    EventTarget ? relatedTarget : ;
}
;
//# sourceMappingURL=events.js.map