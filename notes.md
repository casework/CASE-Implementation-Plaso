

- Why is `fileSystemType` in both `File` and `FileSystem` property bundles?
- Clarifications on when to use "PhoneAccount" or "EmailAccount" vs "Contact" is needed.
- Why is there a separate `isRead` for `SMSMessage`? A regular message like "WhatsApp" could
also have this field.
- Why is there only a `sentTime` timestamp in `Message`? I have other potential timestamps such as "created", "received", "uploaded", "downloaded", "deleted", etc. Having specific hardcoded timestamps in property bundles makes this very limiting. And having some hardcoded timestamps and some not (using Action traces?) is very discombobulated for timelined data. I suggest rethinking this approach to separating timestamp information from data.