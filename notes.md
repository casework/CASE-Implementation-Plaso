

- Why is `fileSystemType` in both `File` and `FileSystem` property bundles?
- Clarifications on when to use "PhoneAccount" or "EmailAccount" vs "Contact" is needed.
- Why is there a separate `isRead` for `SMSMessage`? A regular message like "WhatsApp" could also have this field.
- Why is there only a `sentTime` timestamp in `Message`? I have other potential timestamps such as "created", "received", "uploaded", "downloaded", "deleted", etc. Having specific hardcoded timestamps in property bundles makes this very limiting. And having some hardcoded timestamps and some not (using Action traces?) is very discombobulated for timelined data. I suggest rethinking this approach to separating timestamp information from data.
- What do some of the UcoObject properties mean? eg. `granularMarking` and `objectMarking`
- Why is there an `id` and `type` property in `UcoObject`? Those properties already exists. `id` is the URI of the node itself, `type` is the "rdf:type" property.
- I still can't remember the difference between `result` and `object` properties...
- Why do all UcoObjects have a `name` property? That property only makes sense for things like `Tool`. It doesn't make sense for things like `Trace` and `Action`.
- Why does the `description` property exist? It already exists with "rdfs:comment".