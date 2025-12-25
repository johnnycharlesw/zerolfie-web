"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const events_js_1 = require("./events.js");
events_js_1.EventTarget;
{
    const unsigned, short, ELEMENT_NODE = 1;
    const unsigned, short, ATTRIBUTE_NODE = 2;
    const unsigned, short, TEXT_NODE = 3;
    const unsigned, short, CDATA_SECTION_NODE = 4;
    const unsigned, short, ENTITY_REFERENCE_NODE = 5; // legacy
    const unsigned, short, ENTITY_NODE = 6; // legacy
    const unsigned, short, PROCESSING_INSTRUCTION_NODE = 7;
    const unsigned, short, COMMENT_NODE = 8;
    const unsigned, short, DOCUMENT_NODE = 9;
    const unsigned, short, DOCUMENT_TYPE_NODE = 10;
    const unsigned, short, DOCUMENT_FRAGMENT_NODE = 11;
    const unsigned, short, NOTATION_NODE = 12; // legacy
    unsigned;
    short;
    nodeType;
    string;
    nodeName;
    string;
    baseURI;
    boolean;
    isConnected;
    Document ? ownerDocument : ;
    Node;
    getRootNode(optional, GetRootNodeOptions, options = {});
    Node ? parentNode : ;
    Element ? parentElement : ;
    boolean;
    hasChildNodes();
    [SameObject];
    NodeList;
    childNodes;
    Node ? firstChild : ;
    Node ? lastChild : ;
    Node ? previousSibling : ;
    Node ? nextSibling : ;
    [CEReactions];
    attribute;
    string ? nodeValue : ;
    [CEReactions];
    attribute;
    string ? textContent : ;
    [CEReactions];
    undefined;
    normalize();
    [CEReactions, NewObject];
    Node;
    cloneNode(optional, boolean, subtree = false);
    boolean;
    isEqualNode(Node ? otherNode : );
    boolean;
    isSameNode(Node ? otherNode : ); // legacy alias of ===
    const unsigned, short, DOCUMENT_POSITION_DISCONNECTED = 0x01;
    const unsigned, short, DOCUMENT_POSITION_PRECEDING = 0x02;
    const unsigned, short, DOCUMENT_POSITION_FOLLOWING = 0x04;
    const unsigned, short, DOCUMENT_POSITION_CONTAINS = 0x08;
    const unsigned, short, DOCUMENT_POSITION_CONTAINED_BY = 0x10;
    const unsigned, short, DOCUMENT_POSITION_IMPLEMENTATION_SPECIFIC = 0x20;
    unsigned;
    short;
    compareDocumentPosition(Node, other);
    boolean;
    contains(Node ? other : );
    string ? lookupPrefix(string ? namespace : ) : ;
    string ? lookupNamespaceURI(string ? prefix : ) : ;
    boolean;
    isDefaultNamespace(string ? namespace : );
    [CEReactions];
    Node;
    insertBefore(Node, node, Node ? child : );
    [CEReactions];
    Node;
    appendChild(Node, node);
    [CEReactions];
    Node;
    replaceChild(Node, node, Node, child);
    [CEReactions];
    Node;
    removeChild(Node, child);
}
;
dictionary;
GetRootNodeOptions;
{
    boolean;
    composed = false;
}
;
string;
type;
[SameObject];
Node;
target;
[SameObject];
NodeList;
addedNodes;
[SameObject];
NodeList;
removedNodes;
Node ? previousSibling : ;
Node ? nextSibling : ;
string ? attributeName : ;
string ? attributeNamespace : ;
string ? oldValue : ;
;
class Window {
}
events_js_1.EventTarget;
{
    // the current browsing context
    [LegacyUnforgeable];
    WindowProxy;
    window;
    [Replaceable];
    WindowProxy;
    self;
    [LegacyUnforgeable];
    Document;
    document = globalThis.document;
    attribute;
    string;
    name;
    [PutForwards = href, LegacyUnforgeable];
    Location;
    location;
    History;
    history;
    [Replaceable];
    Navigation;
    navigation;
    CustomElementRegistry;
    customElements;
    [Replaceable];
    locationbar: BarProp;
    [Replaceable];
    menubar: BarProp;
    [Replaceable];
    personalbar: BarProp;
    [Replaceable];
    scrollbars: BarProp;
    [Replaceable];
    statusbar: BarProp;
    [Replaceable];
    toolbar: BarProp;
    attribute;
    string;
    status;
    close();
    {
        __PyBark__.closeThisTab();
    }
    ;
    closed: boolean;
    stop();
    {
        return;
    }
    ;
    focus();
    {
        return;
    }
    ;
    blur();
    {
        return;
    }
    ;
    // other browsing contexts
    [Replaceable];
    frames: WindowProxy;
    [Replaceable];
    length: int;
    [LegacyUnforgeable];
    top ?  : WindowProxy;
    attribute;
    any;
    opener;
    [Replaceable];
    WindowProxy ? parent : ;
    Element ? frameElement : ;
    WindowProxy ? open(optional, string, url = "", optional, string, target = "_blank", optional[LegacyNullToEmptyString], string, features = "") : ;
    // Since this is the global object, the IDL named getter adds a NamedPropertiesObject exotic
    // object on the prototype chain. Indeed, this does not make the global object an exotic object.
    // Indexed access is taken care of by the WindowProxy exotic object.
    getter;
    object(string, name);
    Navigator;
    navigator = globalThis.navigator;
    [Replaceable];
    Navigator;
    clientInformation; // legacy alias of .navigator
    originAgentCluster: boolean;
    // user prompts
    alert(string, message);
    undefined;
    {
        __PyBark__.showDialog(message, type = "infobox");
    }
    ;
    confirm(optional, string, message = "");
    boolean;
    {
        return __PyBark__.showDialog(message, type = "yesno");
    }
    ;
    prompt(optional, string, message = "", optional, string, "");
    {
        return __PyBark__.showDialog(message, type = "ask_for_string");
    }
    ;
    print();
    {
        if (__PyBark__.policies.allowsPrinting) {
            if (globalThis.document) {
                globalThis.document._zlf_invokeEvent("beforeprint");
                __PyBark__.showPrintingUI();
                globalThis.document._zlf_invokeEvent("afterprint");
            }
        }
    }
    ;
    undefined;
    postMessage(any, message, string, targetOrigin, optional, sequence < object > transfer, []);
    undefined;
    postMessage(any, message, optional, WindowPostMessageOptions, options = {});
    // also has obsolete members
}
;
Window;
includes;
GlobalEventHandlers;
Window;
includes;
WindowEventHandlers;
dictionary;
WindowPostMessageOptions: StructuredSerializeOptions;
{
    string;
    targetOrigin = "/";
}
;
//# sourceMappingURL=index.js.map