interface CustomElementRegistry {
  constructor();

  [CEReactions] undefined define(string name, CustomElementConstructor constructor, optional ElementDefinitionOptions options = {});
  (CustomElementConstructor or undefined) get(string name);
  string? getName(CustomElementConstructor constructor);
  Promise<CustomElementConstructor> whenDefined(string name);
  [CEReactions] undefined upgrade(Node root);
  [CEReactions] undefined initialize(Node root);
};

callback CustomElementConstructor = HTMLElement ();

dictionary ElementDefinitionOptions {
  string extends;
};