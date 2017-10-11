import anvil

class Create(object):
    def initialize_and_filter_flags(self, flags, schema):
        if flags is None or flags == {}:
            return {}
        else:
            schema_properties = [key for key in list(schema.get('properties'))]
            anvil.LOG.info('Attempting to filter flags %s for the schema properties %s' % (flags, schema_properties))
            for flag_key in list(flags):
                if flag_key not in schema_properties:
                    anvil.LOG.info('flag %s not in schema...removing from flags' % (flag_key))
                    flags.pop(flag_key)
            return flags

    def create(self, dcc_node_type, flags=None):
        anvil.LOG.info('Attempting to create node type %s with flags %s' % (dcc_node_type, flags))
        function_name_query = 'create_%s' % dcc_node_type
        node = dcc_node_type
        try:
            node = getattr(self, function_name_query)(flags=flags)
        except AttributeError:
            anvil.LOG.warning('No custom method for node type %s found...defaulting...' % dcc_node_type)
        anvil.LOG.info('Created node %s from function %s with flags %s' % (node, function_name_query, flags))
        return node

    def create_transform(self, flags=None):
        return 'group'

    def create_joint(self, flags=None):
        return 'joint'
