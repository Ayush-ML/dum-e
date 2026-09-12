# This Script Handles the State of a Single Joint of the Model as well the Actuator Backend
# It stores the current index, position and velocity of the joint in a frozen dataclass
# The Actuator Backend is responsible for sending the commands to the joint and receiving the feedback from the joint, regardless of the backend, whether it is a Simulation or actual hardware
# The Actuator is Purely a Base Class and exists to be subclassed according to the backend
# It also defines Methods that every single subclass MUST satisfy
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class JointState:
    """A frozen dataclass that stores the current state of a single joint of the model."""   
    index: int
    position: float
    velocity: float

class Actuator(ABC):
    """A base class for actuator backends."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the actuator backend."""

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the actuator backend."""

    @abstractmethod
    def get_joint_state(self) -> list[JointState]:
        """Get the current state of a single joint."""

    @abstractmethod
    def emergency_stop(self) -> None:
        """Stop the actuator immediately in case of an emergency."""

    @abstractmethod
    def set_joint_targets(self, targets: list[float]) -> None:
        """set the target joint angles in radians, one per index, to the actuator backend."""

    @abstractmethod
    def is_connnected(self) -> bool:
        """Check if the actuator backend is connected and test if its commandable"""