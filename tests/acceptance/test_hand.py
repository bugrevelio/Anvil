from six import iteritems
import anvil.node_types as nt
from anvil.utils.scene import print_scene_tree
from anvil.sub_rig_templates import Hand
from tests.base_test import TestBase, cleanup_nodes
import string


class TestHandBase(TestBase):
    name_tokens = {'name': 'hoof', 'purpose': 'mvp'}
    HAND_MERC_JOINTS = ['j_pa_r', 'j_ra_r', 'j_ia_r', 'j_ma_r', 'j_ta_r']

    @classmethod
    def from_template_file(cls, template_file, finger_start_joints=None, **kwargs):
        """

        rt.dcc.scene.fileop(template_file,
                            i=True,
                            type="FBX",
                            ignoreVersion=True,
                            ra=True,
                            mergeNamespacesOnClash=False,
                            options="fbx",
                            pr=True)
        """
        cls.import_template_files(template_file)

        finger_joints = []
        for finger in finger_start_joints:
            finger_joints.append(list(nt.HierarchyChain(finger)))

        rig_instance = Hand(layout_joints=finger_joints, **kwargs)
        rig_instance.build(**kwargs)
        return rig_instance


class TestBuildHand(TestHandBase):
    rig = None

    @classmethod
    def setUpClass(cls):
        super(TestBuildHand, cls).setUpClass()
        try:
            cls.rig = cls.from_template_file(cls.HAND_MERC, cls.HAND_MERC_JOINTS)
        except IndexError:
            print_scene_tree()

    def test_build_no_kwargs_no_errors(self):
        self.assertIsNotNone(self.rig)

    def test_number_of_controls(self):
        controls = [node for key, node in iteritems(self.rig.hierarchy) if isinstance(node, nt.Control)]
        self.assertEqual(len(controls), 0)

    def test_number_of_control_top_groups(self):
        self.assertEqual(len(self.rig.group_controls.get_children()), 10)

    def test_number_of_joint_chains(self):
        self.assertEqual(len(self.rig.group_joints.get_children()), 15)

    def test_number_of_nodes(self):
        self.assertEqual(len(self.rig.group_nodes.get_children()), 5)


class TestBuildDefaultHand(TestHandBase):
    def test_build_with_parent(self):
        with cleanup_nodes():
            parent = nt.Transform.build(name='test')
            rig_instance = self.from_template_file(self.HAND_MERC, self.HAND_MERC_JOINTS, parent=parent)
            self.assertEqual(str(rig_instance.root.get_parent()), str(parent))


class TestGetFingerBaseNames(TestHandBase):
    @classmethod
    def setUpClass(cls):
        super(TestGetFingerBaseNames, cls).setUpClass()
        cleanup_nodes()
        cls.hand = Hand(cls.HAND_MERC_JOINTS)

    def test_default_with_thumb_from_fbx(self):
        self.hand.layout_joints = self.HAND_MERC_JOINTS
        self.hand.has_thumb = True
        self.assertEqual(self.hand.get_finger_base_names(), Hand.DEFAULT_NAMES)

    def test_no_thumb_4(self):
        self.hand.layout_joints = ['a' * x for x in range(4)]
        self.hand.has_thumb = False
        self.assertEqual(self.hand.get_finger_base_names(), Hand.DEFAULT_NAMES[1:5])

    def test_no_thumb_5(self):
        self.hand.layout_joints = ['a' * x for x in range(5)]
        self.hand.has_thumb = False
        self.assertEqual(self.hand.get_finger_base_names(), ['fingerA', 'fingerB', 'fingerC', 'fingerD', 'fingerE'])

    def test_no_thumb_under_5(self):
        self.hand.layout_joints = ['a' * x for x in range(3)]
        self.hand.has_thumb = False
        self.assertEqual(self.hand.get_finger_base_names(), Hand.DEFAULT_NAMES[1:4])

    def test_no_thumb_over_5(self):
        self.hand.layout_joints = ['a' * x for x in range(10)]
        self.has_thumb = False
        self.assertEqual(self.hand.get_finger_base_names(),
                         ['finger' + string.ascii_uppercase[i] for i in range(10)])

    def test_thumb_under_5(self):
        self.hand.layout_joints = ['a' * x for x in range(4)]
        self.hand.has_thumb = True
        self.assertEqual(self.hand.get_finger_base_names(), Hand.DEFAULT_NAMES[:4])

    def test_thumb_over_5(self):
        self.hand.layout_joints = ['a' * x for x in range(10)]
        self.hand.has_thumb = True
        self.assertEqual(self.hand.get_finger_base_names(), ['finger' + string.ascii_uppercase[i] for i in range(10)])