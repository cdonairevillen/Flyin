*This project has been created as part of the 42 curriculum by cdonairevillen.*

# Fly-in Drone Simulator

## Description

This project simulates the movement of multiple drones across a network of zones connected by links. The goal is to model drone traffic, taking into account path cost, capacity constraints, and priority zones. The simulation includes a textual output for turn-by-turn tracking and a graphical visualization to enhance understanding of drone movements.

The project implements:

* A pathfinding system based on a **multi-path Dijkstra algorithm**, considering multiple constraints.
* Dynamic scheduling of drones along paths, respecting capacities of both zones and links.
* A real-time visualization using `pygame`, showing drones moving through zones and along links.

## Instructions

1. **Requirements**

   * Python 3.10+
   * `pygame` library
2. **Installation**

   ```bash
   pip install -r requirements.txt
   ```
3. **Execution**

   ```bash
   python main.py <input_file>
   ```

   The program will first display all drones at the start hub, then simulate each turn until all drones reach the end hub. A `pygame` window will visualize the simulation.

## Algorithm Choices and Implementation Strategy

* **Path Calculation:** Paths are generated using a multi-path variant of **Dijkstra's algorithm**, allowing multiple drones to follow optimal paths based on cost and capacity.
* **Drone Scheduling:** Each drone is assigned to the path with the lowest total time, which includes both the path cost and the current load (assigned drones).
* **Turn Simulation:** Each turn consists of:

  1. Moving drones in transit.
  2. Moving drones that are stationary.
  3. Logging positions and building the output history.
* **Capacity Handling:** The simulation respects the maximum number of drones per zone and per link, using `float("inf")` for unrestricted capacities.
* **Sorting and Comparison:** Drone paths are sorted using the `__lt__` (less-than) method, which allows comparing paths by score for optimal assignment.
* **Data Structures:** Python's `heapq` is used to efficiently manage lists as heaps when needed for path selection.

## Visual Representation

The `pygame` visualizer shows:

* Zones as colored squares (normal, priority, restricted, blocked).
* Links as lines connecting zones with visual indicators for link capacity.
* Drones as moving circles, following smooth animation with ease-in/out interpolation.
* Zone occupancy and drone movements, highlighting collisions and congestion visually.

This visual feedback greatly improves understanding of the simulation dynamics, making it easy to debug and analyze drone traffic.

## Resources

* Python `__hash__` and `__eq__` usage: [Elshad Karimov article](https://elshad-karimov.medium.com/what-is-the-role-of-pythons-hash-and-eq-methods-2ade678c1565)
* Python `heapq` documentation for priority queues
* Python `float("inf")` usage for unbounded capacities
* Python `__lt__` method for object comparison in sorting
* Tutorials on Dijkstra's algorithm and multi-path scheduling
* `pygame` documentation for real-time visualization
* **AI Assistance:** GPT-5 was used to generate type hints, docstrings, and explanations for simulation and visualization modules. No AI was used for the core pathfinding or logic implementation — this was entirely written manually.

## Notes on Research

During the development of this project, significant research was conducted to understand:

* How Python’s `__hash__` and `__eq__` methods work for object comparison in dictionaries and sets.
* How to implement a multi-path version of Dijkstra’s algorithm.
* Efficient drone scheduling using heaps and path scoring.
* Smooth animation techniques for real-time visualization in `pygame`.

These investigations directly influenced design decisions and the internal architecture of the simulation.
