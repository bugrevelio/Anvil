import string
import anvil
import anvil.config as cfg
from base import SubRigTemplate
from digits import Digit


class Hand(SubRigTemplate):
    DEFAULT_NAMES = ["thumb", "index", "middle", "ring", "pinky"]
    CONTROLLER_ATTRIBUTES = {
        "curl_side_bias": None,

    }

    def __init__(self, has_thumb=False, finger_joints=None, **kwargs):
        """ General class for a hand.

        :param has_thumb: bool or int, if this is true will use the first digit as a thumb, if int uses that index
        :param finger_joints: [nt.HierarchyChain or str]: list joint chains to build the fingers on.
        """
        super(Hand, self).__init__(**kwargs)
        self.layout_joints = finger_joints or []
        self.has_thumb = has_thumb
        self.digits = []

    def hook_up_attribute_controls(self, controller):
        controller = anvil.factory(controller)

    def build(self, parent=None, use_layout=True, build_ik=True, build_fk=True, meta_data=None, **kwargs):
        super(Hand, self).build(meta_data=meta_data, parent=parent, **kwargs)
        num_fingers = len(self.layout_joints)
        self.LOG.info('Building %s: %r with %d digits' % (self.__class__.__name__, self, num_fingers))

        meta_data_copy = self.meta_data.copy()
        base_names = self.DEFAULT_NAMES if num_fingers == 5 else [cfg.FINGER + letter for letter in
                                                                  string.uppercase[:num_fingers]]
        for layout_joints, base_name in zip(self.layout_joints, base_names):
            self.LOG.info('Building digit %s from joints %r' % (base_name, layout_joints))
            meta_data_copy[cfg.NAME] = base_name
            digit = Digit(layout_joints, meta_data=meta_data_copy)
            digit.build(parent=self.root, **self.build_kwargs)
            self.digits.append(digit)

        self.rename()

    def rename(self, *input_dicts, **name_tokens):
        super(Hand, self).rename()
        meta_data = self.meta_data.copy()
        meta_data.pop(cfg.NAME)

        for digit in self.digits:
            digit.rename(meta_data)
