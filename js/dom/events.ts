interface Event {
  constructor(string type, optional EventInit eventInitDict = {});

  readonly string type;
  readonly EventTarget? target;
  readonly EventTarget? srcElement; // legacy
  readonly EventTarget? currentTarget;
  sequence<EventTarget> composedPath();

  const NONE: int = 0;
  const CAPTURING_PHASE: int = 1;
  const AT_TARGET: int = 2;
  const BUBBLING_PHASE: int = 3;
  readonly eventPhase: int;

  stopPropagation(){
    return; // stop propogation later
  };

  stopImmediatePropagation(){
    return; // stop propogation later
  };

  readonly bubbles: boolean;
  readonly cancelable: boolean;
  preventDefault(){
    this.defaultPrevented = true;
  };
  defaultPrevented: boolean;
  readonly boolean composed;

  [LegacyUnforgeable] readonly boolean isTrusted;
  readonly DOMHighResTimeStamp timeStamp;

  undefined initEvent(string type, optional boolean bubbles = false, optional boolean cancelable = false); // legacy
};

interface EventInit {
  boolean bubbles = false;
  boolean cancelable = false;
  boolean composed = false;
};

abstract class EventTarget {
  constructor();

  undefined addEventListener(string type, EventListener? callback, optional (AddEventListenerOptions or boolean) options = {});
  undefined removeEventListener(string type, EventListener? callback, optional (EventListenerOptions or boolean) options = {});
  boolean dispatchEvent(Event event);
};

callback interface EventListener {
  undefined handleEvent(Event event);
};

dictionary EventListenerOptions {
  boolean capture = false;
};

interface AddEventListenerOptions : EventListenerOptions {
  passive: boolean;
  boolean once = false;
  AbortSignal signal;
};

abstract class AbortSignal : EventTarget {
  [NewObject] static AbortSignal abort(?reason: any) {
    return new AbortSignal(reason);
  };
  [Exposed=(Window,Worker), NewObject] static AbortSignal timeout([EnforceRange] milliseconds: bigint);
  [NewObject] static AbortSignal _any(sequence<AbortSignal> signals);

  readonly aborted: boolean;
  readonly reason: any;
  throwIfAborted(){
    if (this.aborted) {
      throw new Error("Thrown since it aborted!");
      
    }
  };

  attribute EventHandler onabort;
};

class UIEvent : Event {
  constructor(string type, optional UIEventInit eventInitDict = {}){

  };
  readonly Window? view;
  readonly long detail;
};

dictionary UIEventInit : EventInit {
  Window? view = null;
  long detail = 0;
};

class FocusEvent : UIEvent {
  constructor(string type, optional FocusEventInit eventInitDict = {}){
    super();
  };
  readonly EventTarget? relatedTarget;
};

class MouseEvent : UIEvent {
  constructor(string type, optional MouseEventInit eventInitDict = {}) {
    super();
  };
  readonly screenX: int;
  readonly screenY: int;
  readonly clientX: int;
  readonly clientY: int;
  readonly layerX: int;
  readonly layerY: int;

  readonly ctrlKey: boolean;
  readonly shiftKey: boolean;
  readonly altKey: boolean;
  readonly metaKey: boolean;

  readonly button: int;
  readonly buttons: int;

  readonly relatedTarget?: EventTarget;

  getModifierState(string keyArg): boolean {

  };
};

class WheelEvent : MouseEvent {
  constructor(string type, optional WheelEventInit eventInitDict = {}){
    super();
  };
  const DOM_DELTA_PIXEL: int = 0x00;
  const DOM_DELTA_LINE: int  = 0x01;
  const DOM_DELTA_PAGE: int  = 0x02;

  readonly deltaX: int;
  readonly deltaY: int;
  readonly deltaZ: int;
  readonly deltaMode: int;
};

class InputEvent : UIEvent {
  constructor(string type, optional InputEventInit eventInitDict = {});
  readonly data?: string;
  readonly isComposing: boolean;
  readonly inputType: string;
};

dictionary InputEventInit : UIEventInit {
  data?: string = null;
  isComposing: boolean = false;
  inputType: string = "";
};

interface KeyboardEvent : UIEvent {
  constructor(string type, optional KeyboardEventInit eventInitDict = {});
  // KeyLocationCode
  const unsigned long DOM_KEY_LOCATION_STANDARD = 0x00;
  const unsigned long DOM_KEY_LOCATION_LEFT = 0x01;
  const unsigned long DOM_KEY_LOCATION_RIGHT = 0x02;
  const unsigned long DOM_KEY_LOCATION_NUMPAD = 0x03;

  readonly attribute string key;
  readonly attribute string code;
  readonly attribute unsigned long location;

  readonly attribute boolean ctrlKey;
  readonly attribute boolean shiftKey;
  readonly attribute boolean altKey;
  readonly attribute boolean metaKey;

  readonly attribute boolean repeat;
  readonly attribute boolean isComposing;

  boolean getModifierState(string keyArg);
};

class CompositionEvent : UIEvent {
  constructor(string type, optional CompositionEventInit eventInitDict = {}){

  };
  readonly data: string;
};

dictionary CompositionEventInit : UIEventInit {
  string data = "";
};