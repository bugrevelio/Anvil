import node_types as node_types
import transform


@node_types.register_node
class Joint(transform.Transform):
    dcc_type = 'joint'

    def __init__(self, name, parent=None, flags=None, meta_data=None):
        super(Joint, self).__init__(name, flags=flags, meta_data=meta_data)
