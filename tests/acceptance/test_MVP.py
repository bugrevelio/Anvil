from six import iteritems
import anvil
import anvil.config as cfg
import anvil.node_types as nt
from tests.base_test import TestBase


class TestBaseRig(TestBase):
    name_tokens = {'name': 'eye', 'purpose': 'mvp', 'character': 'bert'}
    test_rig = None

    @classmethod
    def build_dependencies(cls):
        super(TestBaseRig, cls).build_dependencies()
        test_rig = nt.Rig(name_tokens=cls.name_tokens)
        sub_rig = test_rig.build_sub_rig('eyeball', name_tokens={'name': 'eyeball'})
        test_rig.build()
        sub_rig.build_node(nt.Joint, 'joint_eye', parent=sub_rig.group_joints)
        sub_rig.build_node(nt.Control, 'control_eye', parent=sub_rig.group_controls, shape='sphere')
        anvil.runtime.dcc.connections.parent(sub_rig.joint_eye, getattr(sub_rig.control_eye, cfg.CONNECTION_GROUP))
        test_rig.rename()
        cls.test_sub_rig = sub_rig
        cls.test_rig = test_rig
        cls.LOG.info('Built rig for testing %s' % test_rig)
        return test_rig


class TestRigEyeBuild(TestBaseRig):
    def test_control_created(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEqual(self.test_rig.find_node('control_universal'), self.test_rig.control_universal)

    def test_extra_control_created(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEqual(self.test_sub_rig.find_node('control_eye'), self.test_sub_rig.control_eye)

    def test_extra_joint_created(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEqual(self.test_sub_rig.find_node('joint_eye'), self.test_sub_rig.joint_eye)

    def test_constraint(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertTrue(anvil.runtime.dcc.scene.list_scene(type='parentConstraint'))

    def test_hierarchy_exists(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        for key, node in iteritems(self.test_rig.hierarchy):
            self.LOG.info('Checking to see if node %r at key %s exists...' % (node, key))
            self.assertTrue(anvil.runtime.dcc.scene.exists(str(node)))

    def test_hierarchy_count(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEquals(len(list(self.test_rig.hierarchy)), 5)

    def test_sub_rig_hierarchy_count(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEquals(len(list(self.test_rig.sub_rigs['eyeball'].hierarchy)), 8)

    def test_sub_rig_count(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEquals(len(list(self.test_rig.sub_rigs)), 1)


class TestRigRename(TestBaseRig):
    def test_universal_control_name(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEqual(str(self.test_rig.control_universal.control), 'bert_eye_universal_mvp_CTR')

    def test_root_name(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertEqual(str(self.test_rig.root), 'bert_rig_eye_mvp_GRP')

    def test_sub_groups(self):
        if not getattr(self, 'test_sub_rig', None):
            self.build_dependencies()
        self.assertListSame(sorted(['bert_rig_eye_mvp_GRP',
                                    'bert_eye_sub_rigs_mvp_GRP',
                                    'bert_eye_universal_mvp_OGP',
                                    'bert_eye_extras_mvp_GRP',
                                    'bert_eye_model_mvp_GRP']),
                            sorted([str(self.test_rig.hierarchy[node]) for node in self.test_rig.hierarchy]))
