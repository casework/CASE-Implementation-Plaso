

- Why is `fileSystemType` in both `File` and `FileSystem` property bundles?
- Clarifications on when to use "PhoneAccount" or "EmailAccount" vs "Contact" is needed.
- Why is there a separate `isRead` for `SMSMessage`? A regular message like "WhatsApp" could also have this field.
- Why is there only a `sentTime` timestamp in `Message`? I have other potential timestamps such as "created", "received", "uploaded", "downloaded", "deleted", etc. Having specific hardcoded timestamps in property bundles makes this very limiting. And having some hardcoded timestamps and some not (using Action traces?) is very discombobulated for timelined data. I suggest rethinking this approach to separating timestamp information from data.
- What do some of the UcoObject properties mean? eg. `granularMarking` and `objectMarking`
- Why is there an `id` and `type` property in `UcoObject`? Those properties already exists. `id` is the URI of the node itself, `type` is the "rdf:type" property.
- I still can't remember the difference between `result` and `object` properties...
- Why do all UcoObjects have a `name` property? That property only makes sense for things like `Tool`. It doesn't make sense for things like `Trace` and `Action`.
- Why does the `description` property exist? It already exists with "rdfs:comment".

- So DiskPartition has the following properties:

    ```
        - mountPoint
        - partitionID
        - partitionLength
        - partitionOffset
        - spaceLeft
        - spaceUsed
        - totalSpace
        - diskPartitionType
        - createdTime
     ```

    - These properties seem to suggest that this property bundle should be placed in a Trace.
    However, in plaso's use case, it needs to be placed in a Relationship object and only use a subset of these properties
     (image -> partOffset = 4 -> the partition)
    - Should we create two separate property bundles like we did with File and PathRelation?

- I've added LVMVolume property bundle to CASE.
- For the "File" property bundle, what are considered to have a file system type?
    - Besides the obvious ones like NTFS and EXT4 there are also things like TAR and 7z that are included because they have file-like properties (filepath, MAC times, etc)
    - However, do we consider other file systems that don't have the traditional file-like properties but have other properties to extract a file. (eg. SQLiteBlob, Encryption, Compression, etc.)
        - These file types obviously don't have MAC times and filePath, but they have other properties used to grab files.
            - SQLiteBlob uses the parameters: tableName, columnName, and rowCondition or rowIndex
            - Encryption uses the parameters: key, IV, method, and cipher mode
            - Encoding uses the parameters: method
    - Also there are some filesystem types that do not have any extra parameters. (eg. VMDK, VHDI, QCOW, EWF, etc)
        - These file system types usually contain Volumes or Partitions. DFVFS treats these file systems


- I have run into issues dealing with Volumes:
    - How would I convert a DFVFS path spec like the following?:
        ```
            OS: location=C:\image.qcow2
            QCOW: -
            LVM: location=/lvm2, volume_index=1
            TSK: location=/a_dir/a_file.txt
        ```
    - How do I deal with the LVM level? Do I put that in the Relationship object or Trace? or both?
