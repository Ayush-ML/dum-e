# Shared utility functions for working with URDFs and PyBullet.
# Used Across the System to remove redundant code and ensure consistent behavior.
# Only Functions that are used in multiple places should be added here; otherwise, they should be defined in the module that uses them.
import yaml
import pybullet as p


def load_config(config_path: str) -> dict:
    """Loads and parses a YAML config file into a plain dict."""
    with open(config_path) as f:
        return yaml.safe_load(f)

def discover_movable_joints(robot_id: int | None, physics_client_id: int | None = None) -> list[int]:
    """Returns the indices of all non-fixed joints on a loaded URDF body."""
    kwargs = {} if physics_client_id is None else {"physicsClientId": physics_client_id}

    movable = []
    num_joints = p.getNumJoints(robot_id, **kwargs)
    for i in range(num_joints):
        joint_info = p.getJointInfo(robot_id, i, **kwargs)
        joint_type = joint_info[2]
        if joint_type != p.JOINT_FIXED:
            movable.append(i)

    return movable