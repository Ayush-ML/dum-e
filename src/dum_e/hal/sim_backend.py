# This is the Pybullet Simulation Backend for the Actuator Base Class
# It implements the methods defined in the Actuator Base Class and uses Pybullet as the simulation
# It also Implements a new method to figure out which joints of the robot are currently movable and which are fixed

import pybullet as pb
import pybullet_data
import yaml
from dum_e.hal.base import Actuator, JointState


class SimBackend(Actuator):
    """The Simulation Backend for Pybullet using the URDF-described arm, inherited from the Base Actuator class."""

    def __init__(self, urdf_path: str | None = None, use_gui: bool | None = None, gravity_z: float | None = None, max_force: float | None = None) -> None:
        config = self._load_config("config/robot.yaml")["sim"]

        self._urdf_path = urdf_path if urdf_path else config["urdf_path"]
        self._gravity_z = gravity_z if gravity_z is not None else config["gravity_z"]
        self._max_force = max_force if max_force is not None else config["max_joint_force"]
        self._use_gui = use_gui if use_gui is not None else config["use_gui"]

        self._client_id: int | None = None
        self._robot_id: int | None = None
        self._joint_indices: list[int] = []

    @staticmethod 
    def _load_config(config_path: str) -> dict:
        """Loads the Configuration of the YAML File specified in the Path given"""
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _discover_movable_joints(self) -> list[int]:
        """Filter Out Fixed Joints and Discover the movable joints of the robot and return their indices."""

        joint_indices = []
        num_joints = pb.getNumJoints(self._robot_id)
        for i in range(num_joints):
            joint_info = pb.getJointInfo(self._robot_id, i)
            joint_type = joint_info[2]  # Joint type is at index 2
            if joint_type != pb.JOINT_FIXED:
                joint_indices.append(i)

        return joint_indices

    def connect(self) -> None:
        """Connect to the PyBullet Simulation, Setup Required Values and Load the URDF's"""
        mode = pb.GUI if self._use_gui else pb.DIRECT
        self._client_id = pb.connect(mode)  

        pb.setAdditionalSearchPath(pybullet_data.getDataPath())
        pb.setGravity(0, 0, self._gravity_z)
        pb.loadURDF("plane.urdf")

        self._robot_id = pb.loadURDF(self._urdf_path, useFixedBase=True)
        self._joint_indices = self._discover_movable_joints()

    def disconnect(self) -> None:
        """Disconnect from the PyBullet Simulation and Clean Up Completely"""
        if self._client_id is not None:
            pb.disconnect(self._client_id)
        self._client_id = None
        self._robot_id = None
        self._joint_indices = []

    def is_connected(self) -> bool:
        """Check if the Simulation is Connected and Commandable"""
        return self._client_id is not None and self._robot_id is not None
    
    def _require_connection(self) -> None:
        """Ensure that the simulation is connected before performing any operations."""
        if not self.is_connected():
            raise RuntimeError("Simulation backend is not connected.")

    def get_joint_state(self) -> list[JointState]:
        """Get the current state of all movable joints in the simulation."""
        self._require_connection()

        joint_states = []
        for joint_index in self._joint_indices:
            position, velocity, _, _ = pb.getJointState(self._robot_id, joint_index)
            joint_states.append(JointState(index=joint_index, position=position, velocity=velocity))
        return joint_states

    def emergency_stop(self) -> None:
        """Stop the simulation immediately in case of an emergency."""
        if not self.is_connected():
            return
        
        for joint_index in self._joint_indices:
            pb.setJointMotorControl2(self._robot_id, joint_index, pb.VELOCITY_CONTROL, force=self._max_force, targetVelocity=0.0)

    def set_joint_targets(self, targets: list[float]) -> None:
        """Set the target joint angles in radians for all movable joints in the simulation."""
        self._require_connection()

        if len(targets) != len(self._joint_indices):
            raise ValueError(f"Expected {len(self._joint_indices)} targets, but got {len(targets)}.")

        for joint_index, target in zip(self._joint_indices, targets):
            pb.setJointMotorControl2(self._robot_id, joint_index, pb.POSITION_CONTROL, targetPosition=target, force=self._max_force)