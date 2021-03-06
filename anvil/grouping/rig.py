from collections import OrderedDict
from six import iteritems, itervalues
import inspect
import base
import anvil
import anvil.config as cfg
import anvil.objects as ot
import control as ct
from sub_rig import SubRig
from anvil.meta_data import MetaData


class Rig(base.AbstractGrouping):
    """ A fully functional and self-contained rig with all requirements implemented that
        require it to give a performance.  A collection of SubRig(s)
    """
    LOG = anvil.log.obtain_logger(__name__)
    BUILT_IN_NAME_TOKENS = MetaData(base.AbstractGrouping.BUILT_IN_NAME_TOKENS)
    SUB_RIG_BUILD_ORDER = []
    SUB_RIG_BUILD_TABLE = OrderedDict()
    ORDERED_SUB_RIG_KEYS = []
    SUB_GROUPINGS = ['extras', 'model', 'sub_rigs']

    ROOT_NAME_TOKENS = {cfg.RIG_TYPE: cfg.RIG_TYPE, cfg.TYPE: cfg.GROUP_TYPE}
    UNIV_NAME_TOKENS = {cfg.CHILD_TYPE: cfg.UNIVERSAL}

    def __init__(self, character=None, sub_rig_dict=None, *args, **kwargs):
        self.sub_rigs = OrderedDict.fromkeys(self.ORDERED_SUB_RIG_KEYS)
        super(Rig, self).__init__(*args, **kwargs)
        self.name_tokens[cfg.CHARACTER] = character or self.name_tokens.get(cfg.CHARACTER, '')
        self.register_sub_rigs_from_dict(sub_rig_dict)

    def rename(self, *input_dicts, **name_tokens):
        super(Rig, self).rename(*input_dicts, **name_tokens)
        for sub_rig_instance in itervalues(self.sub_rigs):
            sub_rig_instance.rename()  # *input_dicts, **name_tokens)

    def register_sub_rigs_from_dict(self, sub_rig_dict):
        """ Only accepts dictionary with keys that match the built in SUB_RIG_BUILD_TABLE for the given Rig.
            Rig will initialize sub-rigs from the key, value and look up the proper sub-rig class from the build table.
            This is meant to rebuild a rig from a deserialized rig.

        :param sub_rig_dict: dict, key must be in SUB_RIG_BUILD_TABLE and value must be dict or list of joints.
        """
        if sub_rig_dict is None or not isinstance(sub_rig_dict, dict):
            return

        for sub_rig_name, sub_rig_data in iteritems(sub_rig_dict):
            try:
                sub_rig_construction_data = self.SUB_RIG_BUILD_TABLE.get(sub_rig_name)
                sub_rig_class, default_name_tokens = sub_rig_construction_data
                sub_rig_kwargs = sub_rig_data if isinstance(sub_rig_data, dict) else {cfg.LAYOUT: sub_rig_data}
                self.build_sub_rig(sub_rig_name, sub_rig_class, name_tokens=default_name_tokens, **sub_rig_kwargs)
            except TypeError:
                self.warning('Sub rig table entry %r not found in input dict %s', sub_rig_name, sub_rig_dict)

    def build_sub_rig(self, sub_rig_key, sub_rig_candidate=SubRig, **kwargs):
        """ Initializes the given sub rig candidate class with kwargs and stores it in property sub_rigs under the key.

        :param sub_rig_key: str, key to store the sub rig under on the rig.
        :param sub_rig_candidate: anvil.sub_rig, a class that inherits from anvil.sub_rig.
        """
        kwargs[cfg.NAME_TOKENS] = MetaData(self.name_tokens, kwargs.get(cfg.NAME_TOKENS, {}))
        kwargs[cfg.META_DATA] = MetaData(self.meta_data, kwargs.get(cfg.META_DATA, {}))
        if inspect.isclass(sub_rig_candidate) and issubclass(sub_rig_candidate, SubRig):
            self.sub_rigs[sub_rig_key] = sub_rig_candidate(**kwargs)
            return self.sub_rigs[sub_rig_key]

    def build_sub_rigs(self):
        for sub_rig_member in itervalues(self.sub_rigs):
            if not sub_rig_member.is_built:
                self.info('Building sub-rig %s on rig %s', sub_rig_member, self)
                sub_rig_member.build()
            anvil.runtime.dcc.scene.parent(sub_rig_member.root, self.node.group_sub_rigs)

    def auto_color(self):
        super(Rig, self).auto_color()
        for sub_rig_instance in itervalues(self.sub_rigs):
            sub_rig_instance.auto_color()

    def build(self, parent=None, name_tokens=None, **kwargs):
        self.info('Building %s(%r) with parent: %s, name_tokens: %s, and kwargs: %s',
                  self.__class__.__name__, self, parent, name_tokens, kwargs)
        self.name_tokens.update(name_tokens)

        self.build_node(ot.Transform, hierarchy_id='top', name_tokens=self.ROOT_NAME_TOKENS, **kwargs)
        self.root = self.node.top

        self.build_node(ct.Control,
                        hierarchy_id='universal',
                        parent=self.node.top,
                        shape=cfg.DEFAULT_UNIVERSAL_SHAPE,
                        scale=5,
                        name_tokens=self.UNIV_NAME_TOKENS,
                        **kwargs)

        for main_group_type in self.SUB_GROUPINGS:
            self.build_node(ot.Transform,
                            hierarchy_id='%s_%s' % (cfg.GROUP_TYPE, main_group_type),
                            parent=self.control.universal.node.connection_group,
                            name_tokens={cfg.CHILD_TYPE: main_group_type,
                                         cfg.TYPE: cfg.GROUP_TYPE})

        self.build_sub_rigs()
        self.initialize_sub_rig_attributes(self.control.universal.node.control)
        self.connect_rendering_delegate(self.control.universal.node.control)
        self.parent(parent)
        self.rename()
        self.auto_color()

    def __getattr__(self, item):
        try:
            return super(Rig, self).__getattribute__('sub_rigs')[item]
        except KeyError:
            return super(Rig, self).__getattr__(item)
