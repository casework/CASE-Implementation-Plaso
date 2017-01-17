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


def construct(identifier, graph, *args):
    """Constructs a property bundle based on the given identifier.

    Args:
        identifier: The unique identifier to associate to a property bundle to create.
        graph: The graph to create the property bundle.
        *args: Extra arguments used by the given property bundle constructor.

    Returns:
        rdflib.URIRef if successful or None if a constructor is not available.
    """
    if identifier in registry:
        return registry[identifier](graph, *args)
    else:
        return None


@register(dfvfs_definitions.TYPE_INDICATOR_DATA_RANGE)
def DataRange(graph, path_spec):
    pb = BNode()
    graph.add((pb, RDF.type, CASE.DataRange))
    graph.add((pb, CASE.rangeOffset, Literal(path_spec.range_offset)))
    graph.add((pb, CASE.rangeSize, Literal(path_spec.range_size)))
    return pb


@register(dfvfs_definitions.TYPE_INDICATOR_ENCODED_STREAM)
def Encoding(graph, path_spec):
    pb = BNode()
    graph.add((pb, RDF.type, CASE.Encoding))
    encoding_method = mappings.EncodingMethod.get(
        path_spec.encoding_method, path_spec.encoding_method)
    graph.add((pb, CASE.encodingMethod, encoding_method))
    return pb


@register(dfvfs_definitions.TYPE_INDICATOR_ENCRYPTED_STREAM)
def Encryption(graph, path_spec):
    pb = BNode()
    graph.add((pb, RDF.type, CASE.Encryption))
    graph.add((pb, CASE.encryptionIV, Literal(path_spec.initialization_vector)))
    graph.add((pb, CASE.encryptionKey, Literal(path_spec.key)))
    encryption_mode = mappings.EncryptionMode.get(path_spec.cipher_mode)
    if encryption_mode:
        graph.add((pb, CASE.encryptionMode, encryption_mode))
    else:
        raise RuntimeError('Unknown encryption mode.')
    encryption_method = mappings.EncryptionMethod.get(path_spec.encryption_method)
    if encryption_method:
        graph.add((pb, CASE.encryptionMethod, encryption_method))
    else:
        raise RuntimeError('Unknown encryption method.')
    return pb


@register(dfvfs_definitions.TYPE_INDICATOR_SQLITE_BLOB)
def SQLiteBlob(graph, path_spec):
    pb = BNode()
    graph.add((pb, CASE.columnName, Literal(path_spec.column_name)))
    graph.add((pb, CASE.tableName, Literal(path_spec.table_name)))
    if hasattr(path_spec, 'row_index'):
        graph.add((pb, CASE.rowIndex, Literal(path_spec.row_index)))
    elif hasattr(path_spec, 'row_condition'):
        graph.add((pb, CASE.rowCondition, Literal(path_spec.row_condition)))
    return pb

