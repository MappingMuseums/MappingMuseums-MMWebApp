#   $$Author1$:Nick Larsson, Researcher, Dep. of Computer Science and Information Systems at Birkbeck University, London, England, email:nick@dcs.bbk.ac.uk, License:GNU GPLv3
#
#We acknowledge the use of the following software under the terms of the specified licences:
#

#Python Flask - https://flask.palletsprojects.com/en/0.12.x/license/
#
#
#
# - # - # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NodePropertyError(Exception):
    """Basic Node attribute error"""
    pass


class NodeIDAbsentError(NodePropertyError):
    """Exception throwed if a node's identifier is unknown"""
    pass


class NodePropertyAbsentError(NodePropertyError):
    """Exception throwed if a node's data property is not specified"""
    pass


class MultipleRootError(Exception):
    """Exception throwed if more than one root exists in a tree."""
    pass


class DuplicatedNodeIdError(Exception):
    """Exception throwed if an identifier already exists in a tree."""
    pass


class LinkPastRootNodeError(Exception):
    """
    Exception throwed in Tree.link_past_node() if one attempts
    to "link past" the root node of a tree.
    """
    pass


class InvalidLevelNumber(Exception):
    pass


class LoopError(Exception):
    """
    Exception thrown if trying to move node B to node A's position
    while A is B's ancestor.
    """
    pass


