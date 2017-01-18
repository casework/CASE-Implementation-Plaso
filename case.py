"""An API to the CASE ontology."""

import rdflib
from rdflib import RDF

CASE = rdflib.Namespace('http://case.example.org/core#')


class Document(object):

    def __init__(self, graph=None):
        """Initializes the CASE document.

        Args:
            graph: The graph to populate (instance of rdflib.Graph)
                   If not provided, a graph in memory will be used.
        """
        if not graph:
            graph = rdflib.Graph()
        graph.namespace_manager.bind('case', CASE)
        self.graph = graph

    def _json_ld_context(self):
        context = dict(
            (pfx, unicode(ns))
            for (pfx, ns) in self.graph.namespaces() if pfx and
            unicode(ns) != u"http://www.w3.org/XML/1998/namespace")
        context['@vocab'] = str(CASE)
        return context

    def create_trace(self, **properties):
        """Creates and returns a Trace object."""
        return Trace(self.graph, **properties)

    def create_relationship(self, **properties):
        """Creates and returns a Relationship object."""
        return Relationship(self.graph, **properties)

    # We are going to default to json-ld instead of rdflib's default of xml.
    def serialize(self, format='json-ld', **kwargs):
        """Serializes the document's graph to a destination.
        (Follows same arguments as rdflib.Graph().serialize())"""
        if format == 'json-ld' and 'context' not in kwargs:
            kwargs['context'] = self._json_ld_context()
        return self.graph.serialize(format=format, **kwargs)

    def validate(self):
        """Validates that the document follows the CASE ontology."""
        # TODO: Validate document through by parsing the ontology or perhaps
        # using an OWL reasoner.
        pass


class Node(object):
    """Implements a generic node in the graph."""
    RDF_TYPE = None

    # Namespace to use when adding properties that are not of type rdflib.URIRef.
    NAMESPACE = CASE

    def __init__(self, graph, rdf_type=None, **properties):
        """Initializes and adds a node to the graph.
        NOTE: At least the type or a property must be supplied for the Node
        to exist in the graph.

        Args:
            graph: The graph to add this node to. (instance of rdflib.Graph)
            rdf_type: The RDF type to set this node to.
            properties: Extra properties to add to this node.
            (More properties can be set after initialization by using the add() function.)
        """
        super(Node, self).__init__()
        self._node = rdflib.BNode()
        self._graph = graph
        if rdf_type:
            self.add(RDF.type, rdf_type)
        elif self.RDF_TYPE:
            self.add(RDF.type, self.RDF_TYPE)
        for key, value in iter(properties.items()):
            self.add(key, value)

    def add(self, property, value):
        """Adds a property and its value to the node."""
        # Ignore setting properties with a None value.
        if value is None:
            return

        # Lists and other iterables as values are the equivelent of having multiple properties.
        # NOTE: Lists obviously lose their order.
        # TODO: Add support for ordered lists.
        if isinstance(value, (list, tuple, set)):
            for item in value:
                self.add(property, item)
            return

        if isinstance(value, Node):
            value = value._node

        # Convert basic python datatypes to literals.
        elif not isinstance(value, rdflib.term.Node):
            value = rdflib.Literal(value)

        # Automatically convert non-node properties to URIRef using default prefix.
        if not isinstance(property, rdflib.term.Node):
            property = self.NAMESPACE[property]

        self._graph.add((self._node, property, value))


#  ===== Convenience Classes  =====
# TODO: Auto generate these classes by parsing the ontology.

class UcoObject(Node):
    RDF_TYPE = CASE.UcoObject

    def create_property_bundle(self, type=None, **properties):
        """Convenience function for adding property bundles to this Trace.

        Args:
            type: The @type of property bundle (can be of type rdflib.URIRef or string).
            properties: Properties to add to the created property bundle.

        Returns:
            The property bundle created (instance of PropertyBundle).
        """
        # Add case prefix to non URIRef to allow abstraction from rdflib.
        if not isinstance(type, rdflib.term.Node):
            type = CASE[type]
        pb = PropertyBundle(self._graph, rdf_type=type, **properties)
        self.add(CASE.propertyBundle, pb)
        return pb


class Trace(UcoObject):
    RDF_TYPE = CASE.Trace


class Relationship(UcoObject):
    RDF_TYPE = CASE.Relationship


class PropertyBundle(Node):
    RDF_TYPE = CASE.PropertyBundle

