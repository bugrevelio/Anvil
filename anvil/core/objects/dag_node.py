import node_types as node_types
import unicode_delegate as unicode_delegate


@node_types.register_node
class DagNode(unicode_delegate.UnicodeDelegate):
    def __init__(self, node_unicode_proxy, flags=None, metaData=None):
        self._metaData = metaData
        self._flags = flags
        super(DagNode, self).__init__(node_unicode_proxy)
