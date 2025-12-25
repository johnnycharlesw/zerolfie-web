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
  readonly string nodeName;

  readonly string baseURI;

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

  [CEReactions] attribute string? nodeValue;
  [CEReactions] attribute string? textContent;
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

  string? lookupPrefix(string? namespace);
  string? lookupNamespaceURI(string? prefix);
  boolean isDefaultNamespace(string? namespace);

  [CEReactions] Node insertBefore(Node node, Node? child);
  [CEReactions] Node appendChild(Node node);
  [CEReactions] Node replaceChild(Node node, Node child);
  [CEReactions] Node removeChild(Node child);
};

dictionary GetRootNodeOptions {
  boolean composed = false;
};

interface MutationRecord {
  readonly string type;
  [SameObject] readonly Node target;
  [SameObject] readonly NodeList addedNodes;
  [SameObject] readonly NodeList removedNodes;
  readonly Node? previousSibling;
  readonly Node? nextSibling;
  readonly string? attributeName;
  readonly string? attributeNamespace;
  readonly string? oldValue;
};

abstract class Window: EventTarget {
  // the current browsing context
  [LegacyUnforgeable] readonly WindowProxy window;
  [Replaceable] readonly WindowProxy self;
  [LegacyUnforgeable] readonly Document document = globalThis.document;
  attribute string name; 
  [PutForwards=href, LegacyUnforgeable] readonly Location location;
  readonly History history;
  [Replaceable] readonly Navigation navigation;
  readonly CustomElementRegistry customElements;
  [Replaceable] readonly locationbar: BarProp;
  [Replaceable] readonly menubar: BarProp;
  [Replaceable] readonly personalbar: BarProp;
  [Replaceable] readonly scrollbars: BarProp;
  [Replaceable] readonly statusbar: BarProp;
  [Replaceable] readonly toolbar: BarProp;
  attribute string status;
  close(){
    __PyBark__.closeThisTab();
  };
  readonly closed: boolean;
  stop(){
    return;
  };
  focus(){
    return;
  };
  blur(){
    return;
  };

  // other browsing contexts
  [Replaceable] readonly frames: WindowProxy;
  [Replaceable] readonly length: int;
  [LegacyUnforgeable] readonly top?: WindowProxy;
  attribute any opener;
  [Replaceable] readonly WindowProxy? parent;
  readonly Element? frameElement;
  WindowProxy? open(optional string url = "", optional string target = "_blank", optional [LegacyNullToEmptyString] string features = "");

  // Since this is the global object, the IDL named getter adds a NamedPropertiesObject exotic
  // object on the prototype chain. Indeed, this does not make the global object an exotic object.
  // Indexed access is taken care of by the WindowProxy exotic object.
  getter object (string name);

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

  undefined postMessage(any message, string targetOrigin, optional sequence<object> transfer = []);
  undefined postMessage(any message, optional WindowPostMessageOptions options = {});

  // also has obsolete members
};
Window includes GlobalEventHandlers;
Window includes WindowEventHandlers;

dictionary WindowPostMessageOptions : StructuredSerializeOptions {
  string targetOrigin = "/";
};