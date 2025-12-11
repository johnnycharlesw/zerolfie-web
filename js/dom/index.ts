import { EventTarget } from "./events.js";
interface Node : EventTarget {
  const unsigned short ELEMENT_NODE = 1;
  const unsigned short ATTRIBUTE_NODE = 2;
  const unsigned short TEXT_NODE = 3;
  const unsigned short CDATA_SECTION_NODE = 4;
  const unsigned short ENTITY_REFERENCE_NODE = 5; // legacy
  const unsigned short ENTITY_NODE = 6; // legacy
  const unsigned short PROCESSING_INSTRUCTION_NODE = 7;
  const unsigned short COMMENT_NODE = 8;
  const unsigned short DOCUMENT_NODE = 9;
  const unsigned short DOCUMENT_TYPE_NODE = 10;
  const unsigned short DOCUMENT_FRAGMENT_NODE = 11;
  const unsigned short NOTATION_NODE = 12; // legacy
  readonly unsigned short nodeType;
  readonly DOMString nodeName;

  readonly USVString baseURI;

  readonly boolean isConnected;
  readonly Document? ownerDocument;
  Node getRootNode(optional GetRootNodeOptions options = {});
  readonly Node? parentNode;
  readonly Element? parentElement;
  boolean hasChildNodes();
  [SameObject] readonly NodeList childNodes;
  readonly Node? firstChild;
  readonly Node? lastChild;
  readonly Node? previousSibling;
  readonly Node? nextSibling;

  [CEReactions] attribute DOMString? nodeValue;
  [CEReactions] attribute DOMString? textContent;
  [CEReactions] undefined normalize();

  [CEReactions, NewObject] Node cloneNode(optional boolean subtree = false);
  boolean isEqualNode(Node? otherNode);
  boolean isSameNode(Node? otherNode); // legacy alias of ===

  const unsigned short DOCUMENT_POSITION_DISCONNECTED = 0x01;
  const unsigned short DOCUMENT_POSITION_PRECEDING = 0x02;
  const unsigned short DOCUMENT_POSITION_FOLLOWING = 0x04;
  const unsigned short DOCUMENT_POSITION_CONTAINS = 0x08;
  const unsigned short DOCUMENT_POSITION_CONTAINED_BY = 0x10;
  const unsigned short DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC = 0x20;
  unsigned short compareDocumentPosition(Node other);
  boolean contains(Node? other);

  DOMString? lookupPrefix(DOMString? namespace);
  DOMString? lookupNamespaceURI(DOMString? prefix);
  boolean isDefaultNamespace(DOMString? namespace);

  [CEReactions] Node insertBefore(Node node, Node? child);
  [CEReactions] Node appendChild(Node node);
  [CEReactions] Node replaceChild(Node node, Node child);
  [CEReactions] Node removeChild(Node child);
};

dictionary GetRootNodeOptions {
  boolean composed = false;
};

interface MutationRecord {
  readonly DOMString type;
  [SameObject] readonly Node target;
  [SameObject] readonly NodeList addedNodes;
  [SameObject] readonly NodeList removedNodes;
  readonly Node? previousSibling;
  readonly Node? nextSibling;
  readonly DOMString? attributeName;
  readonly DOMString? attributeNamespace;
  readonly DOMString? oldValue;
};

abstract class Window: EventTarget {
  // the current browsing context
  [LegacyUnforgeable] readonly WindowProxy window;
  [Replaceable] readonly WindowProxy self;
  [LegacyUnforgeable] readonly Document document = globalThis.document;
  attribute DOMString name; 
  [PutForwards=href, LegacyUnforgeable] readonly Location location;
  readonly History history;
  [Replaceable] readonly Navigation navigation;
  readonly CustomElementRegistry customElements;
  [Replaceable] readonly BarProp locationbar;
  [Replaceable] readonly BarProp menubar;
  [Replaceable] readonly BarProp personalbar;
  [Replaceable] readonly BarProp scrollbars;
  [Replaceable] readonly BarProp statusbar;
  [Replaceable] readonly BarProp toolbar;
  attribute DOMString status;
  close(){
    __PyBark__.closeThisTab();
  };
  readonly boolean closed;
  undefined stop();
  undefined focus();
  undefined blur();

  // other browsing contexts
  [Replaceable] readonly WindowProxy frames;
  [Replaceable] readonly unsigned long length;
  [LegacyUnforgeable] readonly WindowProxy? top;
  attribute any opener;
  [Replaceable] readonly WindowProxy? parent;
  readonly Element? frameElement;
  WindowProxy? open(optional USVString url = "", optional DOMString target = "_blank", optional [LegacyNullToEmptyString] DOMString features = "");

  // Since this is the global object, the IDL named getter adds a NamedPropertiesObject exotic
  // object on the prototype chain. Indeed, this does not make the global object an exotic object.
  // Indexed access is taken care of by the WindowProxy exotic object.
  getter object (DOMString name);

  // the user agent
  readonly Navigator navigator = globalThis.navigator;
  [Replaceable] readonly Navigator clientInformation; // legacy alias of .navigator
  readonly originAgentCluster: boolean;

  // user prompts
  alert(string message): undefined {
    __PyBark__.showDialog(message, type="infobox");
  };

  confirm(optional string message = ""): boolean {
    return __PyBark__.showDialog(message, type="yesno");
  };
  prompt(optional string message = "", optional string default = ""){
    return __PyBark__.showDialog(message, type="ask_for_string");
  };
  print(){
    if (__PyBark__.policies.allowsPrinting) {
        if (globalThis.document) {
            globalThis.document._zlf_invokeEvent("beforeprint");
            __PyBark__.showPrintingUI();
            globalThis.document._zlf_invokeEvent("afterprint");
        }
    }
  };

  undefined postMessage(any message, USVString targetOrigin, optional sequence<object> transfer = []);
  undefined postMessage(any message, optional WindowPostMessageOptions options = {});

  // also has obsolete members
};
Window includes GlobalEventHandlers;
Window includes WindowEventHandlers;

dictionary WindowPostMessageOptions : StructuredSerializeOptions {
  USVString targetOrigin = "/";
};