---
sidebar_position: 2
---

# ROS 2 Fundamentals

## What is ROS 2?

ROS 2 (Robot Operating System 2) is the next generation of ROS, designed to address the limitations of ROS 1 while maintaining its core philosophy of code reuse and modularity.

## Key Concepts

### Nodes

A **node** is a process that performs computation. Nodes are combined into a graph and communicate with one another using topics, services, or actions.

```python
import rclpy
from rclpy.node import Node

class MyNode(Node):
    def __init__(self):
        super().__init__('my_node')
        self.get_logger().info('Node started!')

def main():
    rclpy.init()
    node = MyNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### Topics

**Topics** are named buses over which nodes exchange messages. Topics have one or more publishers and one or more subscribers.

### Services

**Services** are another method of communication for nodes in the ROS graph. Services are based on a call-and-response model, unlike topics.

## ROS 2 Architecture

ROS 2 uses a distributed architecture where:

- **Nodes** communicate through a **DDS (Data Distribution Service)** middleware
- **Topics** enable publish-subscribe communication
- **Services** enable request-response communication
- **Actions** enable long-running tasks with feedback

## Installation

### Ubuntu 22.04

```bash
sudo apt update
sudo apt install ros-humble-desktop
source /opt/ros/humble/setup.bash
```

### Verify Installation

```bash
ros2 --help
```

## Next Steps

In the next chapter, we'll dive deeper into creating nodes, topics, and services.

