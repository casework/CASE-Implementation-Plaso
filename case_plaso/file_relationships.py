"""Contains constructors for converting dfvfs path specs into CASE property bundles."""

from case import CASE
from dfvfs.lib import lvm
from dfvfs.lib import definitions as dfvfs_definitions

from case_plaso import mappings, PLASO


# Register functions based on indicators.
registry = {}
def register(identifier):
    def func_wrapper(func):
        registry[identifier] = func
        return func
    return func_wrapper


def construct(identifier, uco_object, *args):
    """Constructs property bundles based on the given identifier.

    Args:
        identifier: The unique identifier to associate to a property bundle to create.
        uco_object: The uco_object to place the property bundles in.
        *args: Extra arguments used by the given property bundle constructor.
    """
    if identifier in registry:
        registry[identifier](uco_object, *args)


@register(dfvfs_definitions.TYPE_INDICATOR_BDE)
def BDE(uco_object, path_spec):
    uco_object.create_property_bundle(
        'BDEVolume',
        password=path_spec.password,
        recoveryPassword=path_spec.resovery_password,
        startupKey=path_spec.startup_key)


# NOTE: DFVFS treats GZIP as a file system, but CASE treats it as a compression type.
@register(dfvfs_definitions.TYPE_INDICATOR_GZIP)
@register(dfvfs_definitions.TYPE_INDICATOR_COMPRESSED_STREAM)
def Compression(uco_object, path_spec):
    if path_spec.type_indicator == dfvfs_definitions.TYPE_INDICATOR_GZIP:
        compression_method = CASE.GZIP
    else:
        try:
            compression_method = mappings.CompressionMethod[path_spec.compression_method]
        except KeyError:
            raise RuntimeError(
                'Unsupported compression method: {}'.format(path_spec.compression_method))
    uco_object.create_property_bundle(
        'Compression',
        compressionMethod=compression_method)


@register(dfvfs_definitions.TYPE_INDICATOR_DATA_RANGE)
def DataRange(uco_object, path_spec):
    uco_object.create_property_bundle(
        'DataRange',
        rangeOffset=path_spec.range_offset,
        rangeSize=path_spec.range_size)


@register(dfvfs_definitions.TYPE_INDICATOR_ENCODED_STREAM)
def Encoding(uco_object, path_spec):
    uco_object.create_property_bundle(
        'Encoding',
        encodingMethod=mappings.EncodingMethod[path_spec.encoding_method])


@register(dfvfs_definitions.TYPE_INDICATOR_ENCRYPTED_STREAM)
def Encryption(uco_object, path_spec):
    uco_object.create_property_bundle(
        'Encryption',
        encryptionIV=path_spec.initialization_vector,
        encryptionKey=path_spec.key,
        encryptionMode=mappings.EncryptionMode[path_spec.cipher_mode],
        encryptionMethod=mappings.EncryptionMethod[path_spec.encryption_method])


@register(dfvfs_definitions.TYPE_INDICATOR_FVDE)
def FVDE(uco_object, path_spec):
    uco_object.create_property_bundle(
        'FVDEEncryption',
        encryptedRootPlist=path_spec.encrypted_root_plist,
        password=path_spec.password,
        recoveryPassword=path_spec.recovery_password)


@register(dfvfs_definitions.TYPE_INDICATOR_LVM)
def LVM(uco_object, path_spec):
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)
    uco_object.create_property_bundle(
        'LVMVolume',
        volumeIndex=volume_index)


# TODO: Not really sure how to deal with this one. This is just a guess...
# NOTE: Mount is not allowed to have a parent, so this should only exist on the Trace.
@register(dfvfs_definitions.TYPE_INDICATOR_MOUNT)
def Mount(uco_object, path_spec):
    uco_object.create_property_bundle(
        'Volume',
        volumeID=path_spec.identifier)


@register(dfvfs_definitions.TYPE_INDICATOR_NTFS)
def NTFS(uco_object, path_spec):
    uco_object.create_property_bundle(
        'NTFSFileSystem',
        alternateDataStream=path_spec.data_stream,
        # TODO: These attributes don't technically exist in the CASE property bundle...
        # I assume these attributes are in someway associated with the fileID found in
        # event_exporters.ntfs
        MFTAttribute=path_spec.mft_attribute,
        MFTEntry=path_spec.mft_entry)
    # File path will be dealt with by filestat event exporter.


@register(dfvfs_definitions.TYPE_INDICATOR_SQLITE_BLOB)
def SQLiteBlob(uco_object, path_spec):
    pb = uco_object.create_property_bundle(
        'SQLiteBlob',
        columnName=path_spec.column_name,
        tableName=path_spec.table_name)
    if hasattr(path_spec, 'row_index'):
        pb.add('rowIndex', path_spec.row_index)
    elif hasattr(path_spec, 'row_condition'):
        pb.add('rowCondition', ' '.join(path_spec.row_condition))


@register(dfvfs_definitions.TYPE_INDICATOR_TSK)
def TSK(uco_object, path_spec):
    # NOTE: This is an example of extending case using our own custom property bundle.
    uco_object.create_property_bundle(
        PLASO.TSK,
        dataStream=getattr(path_spec, 'data_stream'),
        inode=path_spec.inode)


# TODO: See note on DiskPartition in notes.md
@register(dfvfs_definitions.TYPE_INDICATOR_TSK_PARTITION)
def TSKPartition(uco_object, path_spec):
    part_index = getattr(path_spec, 'part_index', None)
    location = getattr(path_spec, 'location', None)
    if not part_index and location and location.startswith('/p'):
        try:
            part_index = int(location[2:], 10) - 1
        except KeyError:
            pass
    uco_object.create_property_bundle(
        'DiskPartition',
        paritionOffset=path_spec.start_offset,
        partitionID=part_index)  # TODO: I'm pretty sure this is correct...


@register(dfvfs_definitions.TYPE_INDICATOR_VSHADOW)
def VShadow(uco_object, path_spec):
    uco_object.create_property_bundle(
        'VShadow',
        snapshotID=path_spec.store_index)
    # File path will be dealt with by filestat event exporter.
