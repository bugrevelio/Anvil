from six import iteritems

import anvil
import anvil.runtime as runtime


class UnicodeDelegate(object):
    dcc_type = None

    def __init__(self, node_unicode_proxy, meta_data=None, **flags):
        """ All nodes must be initialized with a string representation that the encompassing platform
            uses as DAG path representation for the object.

        :param node_unicode_proxy: str, DAG path to the object we want to encapsulate
        :param flags: dict, creation flags specific for the platform environment node creation function
        :param meta_data: dict, any object specific meta data we want to record
        """
        anvil.LOG.info('Initializing node %s with ID %s' % (self.__class__, node_unicode_proxy))
        self._dcc_id = runtime.dcc.scene.get_persistent_id(node_unicode_proxy)
        self._api_class_instance = None

        self.flags = flags or {}
        self.meta_data = meta_data or {}

    @classmethod
    def build(cls, meta_data=None, **flags):
        cls.convert_subclass_kwargs(flags)
        dcc_instance = runtime.dcc.create.create(cls.dcc_type, flags=flags)
        instance = cls(dcc_instance, meta_data=meta_data, **flags)

        # If the instance isn't a string we can assume it's some API class instance we can use later.
        if not isinstance(dcc_instance, str):
            instance._api_class_instance = dcc_instance
        return instance

    @classmethod
    def convert_subclass_kwargs(cls, flags):
        if isinstance(flags, dict):
            for k, v in iteritems(flags):
                try:
                    flags[k] = str(v.name())
                    anvil.LOG.info(
                        'Converted internal class %s from kwarg %s from %r to %r' % (type(v), k, v, v.name()))
                except (AttributeError, TypeError):
                    pass

    def __getattr__(self, item):
        try:
            return super(UnicodeDelegate, self).__getattribute__(item)

        except AttributeError:
            def to_camel_case(input_string):
                tokens = input_string.split('_')
                return tokens[0] + ''.join([token.capitalize() for token in tokens[1:]])

            platform_class_instance = super(UnicodeDelegate, self).__getattribute__('_api_class_instance')
            try:
                return platform_class_instance.__getattr__(item)
            except AttributeError:
                return platform_class_instance.__getattr__(to_camel_case(item))