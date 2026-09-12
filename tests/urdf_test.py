# Validates that dum_e_arm.urdf loads correctly and exposes the joints tructure the rest of the system assumes.
# It also checks the inertia of the joint structure to be 0

import pybullet as p
import pytest

EXPECTED_MOVABLE_JOINT_NAMES = [
    "base_rotate",
    "shoulder_pitch",
    "elbow_pitch",
    "wrist_pitch",
    "gripper_pinch",
]


@pytest.fixture
def loaded_robot():
    client_id = p.connect(p.DIRECT)
    robot_id = p.loadURDF("urdf/dum_e_arm.urdf", useFixedBase=True)
    yield robot_id
    p.disconnect(client_id)


def test_urdf_loads_without_error(loaded_robot):
    """Check if URDF loads correctly"""
    assert loaded_robot is not None

def test_movable_joint_count_and_names(loaded_robot):
    """Tests how many joints are movable and whether their names match"""
    movable_names = []
    for i in range(p.getNumJoints(loaded_robot)):
        joint_info = p.getJointInfo(loaded_robot, i)
        if joint_info[2] != p.JOINT_FIXED:
            movable_names.append(joint_info[1].decode("utf-8"))

    assert movable_names == EXPECTED_MOVABLE_JOINT_NAMES


def test_no_joint_has_zero_inertia(loaded_robot):
    """Checks if the URDF has No Inertia"""
    for i in range(p.getNumJoints(loaded_robot)):
        dynamics_info = p.getDynamicsInfo(loaded_robot, i)
        mass = dynamics_info[0]
        assert mass > 0.0, f"Link index {i} has zero or missing mass"