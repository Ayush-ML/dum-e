# This Script is a Test script for the Pybullet Simulation backend.
# They use the pytest framework to run the tests. The tests are designed to check the functionality of the Pybullet Simulation backend.
# They run in Headless DIRECT mode to make it fast without any overhead
# It uses a minimal tets URDF
import pytest
import pybullet as pb
from dum_e.hal.sim_backend import SimBackend


# A Small URDF for Testing Purposes
_TEST_URDF = """<?xml version="1.0"?>
<robot name="test_arm">
  <link name="base_link"/>
  <link name="link1"/>
  <link name="link2"/>
  <joint name="joint1" type="revolute">
    <parent link="base_link"/>
    <child link="link1"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="50" velocity="1"/>
  </joint>
  <joint name="joint2" type="revolute">
    <parent link="link1"/>
    <child link="link2"/>
    <axis xyz="0 0 1"/>
    <limit lower="-3.14" upper="3.14" effort="50" velocity="1"/>
  </joint>
</robot>
"""

@pytest.fixture
def test_urdf_path(tmp_path):
    """Fixture to create a temporary URDF file for testing."""
    urdf_file = tmp_path / "test_arm.urdf"
    urdf_file.write_text(_TEST_URDF)
    return str(urdf_file)

@pytest.fixture
def sim_backend(test_urdf_path):
    """Fixture to create and connect the SimBackend for testing."""
    backend = SimBackend(urdf_path=test_urdf_path, use_gui=False)
    backend.connect()
    yield backend
    backend.disconnect()

def test_joint_discovery(sim_backend):
    """Test that the SimBackend correctly discovers movable joints."""
    joint_states = sim_backend.get_joint_state()  
    assert len(joint_states) == 2  

def test_connect_lifecycle(test_urdf_path):
    """Test the connect and disconnect lifecycle of the SimBackend."""
    backend = SimBackend(urdf_path=test_urdf_path, use_gui=False)

    assert not backend.is_connected()  
    backend.connect()
    assert backend.is_connected()  
    backend.disconnect()
    assert not backend.is_connected()

def test_set_joint_targets(sim_backend):
    """Test setting joint targets in the SimBackend."""
    with pytest.raises(ValueError):
        sim_backend.set_joint_targets([0.1, 0.2, 0.3])  

def test_arm_movement(sim_backend):
    """Test that the arm can move to specified joint targets."""
    target = 1.0
    sim_backend.set_joint_targets([target, 0])

    for _ in range(240):  
        pb.stepSimulation()

    joint_states = sim_backend.get_joint_state()
    joint1_position = joint_states[0].position

    assert joint1_position == pytest.approx(target, abs=0.05)

def test_emergency_stop():
    """Test the emergency stop functionality of the SimBackend."""
    backend = SimBackend(urdf_path=None, use_gui=False)
    backend.emergency_stop()

def test_requires_connection(test_urdf_path):
    """Test that operations requiring connection raise an error when not connected."""
    backend = SimBackend(urdf_path=test_urdf_path, use_gui=False)

    with pytest.raises(RuntimeError):
        backend.get_joint_state()