from base_test import TestBase
import anvil
import anvil.core.objects.node_types as nt


class TestBaseRig(TestBase):
    def setUp(self):
        super(TestBaseRig, self).setUp()

    @staticmethod
    def encapsulation_node_creation():
        return {'node_dag': anvil.core.objects.curve.Curve.build(),
                'control_offset_grp': anvil.core.objects.transform.Transform.build(),
                'control_con_grp': anvil.core.objects.transform.Transform.build()
                }

class TestRigBuild(TestBaseRig):
    def test_default(self):
        test_rig = anvil.core.collections.rig.Rig([])

    def test_curve(self):
        point = {'point': [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]]}
        nt.Curve.build(flags=point)

