interface Event {
  constructor(DOMString type, optional EventInit eventInitDict = {});

  readonly DOMString type;
  readonly EventTarget? target;
  readonly EventTarget? srcElement; // legacy
  readonly EventTarget? currentTarget;
  sequence<EventTarget> composedPath();

  const unsigned short NONE = 0;
  const unsigned short CAPTURING_PHASE = 1;
  const unsigned short AT_TARGET = 2;
  const unsigned short BUBBLING_PHASE = 3;
  readonly unsigned short eventPhase;

  undefined stopPropagation();
           attribute boolean cancelBubble; // legacy alias of .stopPropagation()
  undefined stopImmediatePropagation();

  readonly boolean bubbles;
  readonly boolean cancelable;
           attribute boolean returnValue;  // legacy
  undefined preventDefault();
  readonly boolean defaultPrevented;
  readonly boolean composed;

  [LegacyUnforgeable] readonly boolean isTrusted;
  readonly DOMHighResTimeStamp timeStamp;

  undefined initEvent(DOMString type, optional boolean bubbles = false, optional boolean cancelable = false); // legacy
};

dictionary EventInit {
  boolean bubbles = false;
  boolean cancelable = false;
  boolean composed = false;
};

interface EventTarget {
  constructor();

  undefined addEventListener(DOMString type, EventListener? callback, optional (AddEventListenerOptions or boolean) options = {});
  undefined removeEventListener(DOMString type, EventListener? callback, optional (EventListenerOptions or boolean) options = {});
  boolean dispatchEvent(Event event);
};

callback interface EventListener {
  undefined handleEvent(Event event);
};

dictionary EventListenerOptions {
  boolean capture = false;
};

dictionary AddEventListenerOptions : EventListenerOptions {
  boolean passive;
  boolean once = false;
  AbortSignal signal;
};

abstract class AbortSignal : EventTarget {
  [NewObject] static AbortSignal abort(?reason: any) {
    return new AbortSignal(reason);
  };
  [Exposed=(Window,Worker), NewObject] static AbortSignal timeout([EnforceRange] unsigned long long milliseconds);
  [NewObject] static AbortSignal _any(sequence<AbortSignal> signals);

  readonly boolean aborted;
  readonly any reason;
  undefined throwIfAborted();

  attribute EventHandler onabort;
};

abstract class UIEvent : Event {
  constructor(DOMString type, optional UIEventInit eventInitDict = {}){

  };
  readonly Window? view;
  readonly long detail;
};

dictionary UIEventInit : EventInit {
  Window? view = null;
  long detail = 0;
};

abstract class FocusEvent : UIEvent {
  constructor(DOMString type, optional FocusEventInit eventInitDict = {});
  readonly EventTarget? relatedTarget;
};