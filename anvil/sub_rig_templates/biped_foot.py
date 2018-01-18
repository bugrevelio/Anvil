from base import SubRigTemplate
import anvil.node_types as nt
import anvil.config as cfg


class BipedFoot(SubRigTemplate):
    TOE_TOKEN = 'toe'
    BALL_TOKEN = 'ball'
    ANKLE_TOKEN = 'ankle'
    HEEL_TOKEN = 'heel'
    OUTSOLE_TOKEN = 'outsole'
    INSOLE_TOKEN = 'insole'
    BUILT_IN_META_DATA = SubRigTemplate.BUILT_IN_META_DATA.merge({cfg.NAME: cfg.FOOT}, new=True)

    def __init__(self, heel=None, outsole=None, insole=None, *args, **kwargs):
        super(BipedFoot, self).__init__(*args, **kwargs)
        self.ankle, self.ball, self.toe, self.toe_end = self.layout_joints
        self.heel = heel
        self.outsole = outsole
        self.insole = insole

    def build(self, parent=None, meta_data=None, **kwargs):
        super(BipedFoot, self).build(meta_data=meta_data, parent=parent, **kwargs)
        last = self.group_controls
        for reference_object, label in zip([self.ankle, self.ball, self.toe, self.heel],
                                           [self.ANKLE_TOKEN, self.BALL_TOKEN, self.TOE_TOKEN, self.HEEL_TOKEN]):
            shape = '%s_%s' % (cfg.CIRCLE, cfg.X) if not label == self.ANKLE else '_'.join(
                [s for s in [self.meta_data.get(cfg.SIDE), cfg.FOOT] if s])

            control = self.build_node(nt.Control, '%s_%s' % (cfg.CONTROL_TYPE, label),
                                      shape=shape,
                                      reference_object=reference_object,
                                      parent=last,
                                      name_tokens=self.name_tokens + {cfg.NAME: label},
                                      meta_data=self.meta_data)
            # if label == self.ANKLE_TOKEN:
            # control.offset_group.translate_node(absolute=True)
            last = control.connection_group

        toe_ball_chain = nt.HierarchyChain(*self.layout_joints[1:], node_filter=cfg.JOINT_TYPE)
        ball_handle, ball_effector = toe_ball_chain.build_ik(solver=cfg.IK_SC_SOLVER)
        self.register_node('%s_%s' % (self.meta_data.name, cfg.IK_HANDLE), ball_handle)
        self.register_node('%s_%s' % (self.meta_data.name, cfg.IK_EFFECTOR), ball_effector)

        self.rename()
