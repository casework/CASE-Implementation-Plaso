"""Contains constructors for converting dfvfs and plaso entities into CASE property bundles."""

from rdflib import RDF, Literal, BNode
from dfvfs.lib import definitions as dfvfs_definitions

from case_plaso import CASE, mappings


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


@register('fs:stat:ntfs')
def MftRecord(uco_object, event):
    uco_object.create_property_bundle(
        'MftRecord',
        mftFileID=getattr(event, 'file_reference', None),
        mftFlags=getattr(event, 'file_attribute_flags', None),
        mftParentID=getattr(event, 'parent_file_reference', None))

