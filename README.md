# Slime-Mold-Simulation
Visualization of the Dijkstra's algorithm in a grid-based environment. Every step is displayed by highlighting visited cells, simulating a slime-like growth.
The visualization tries to imitate the movement of Physarum polycephalum. This project is inspired by multiple science experiments showing the ability of slime molds to navigate the quickest route through a maze to get food. The program allows you to draw custom barriers and start/end points.

[Watch Video](https://vimeo.com/833366917)

<img src="https://github.com/SMollov/Slime-Mold-Simulation/blob/main/media/0.png?raw=true" width="45%"></img> <img src="https://github.com/SMollov/Slime-Mold-Simulation/blob/main/media/4.png?raw=true" width="45%"></img> <img src="https://github.com/SMollov/Slime-Mold-Simulation/blob/main/media/2.png?raw=true" width="45%"></img> <img src="https://github.com/SMollov/Slime-Mold-Simulation/blob/main/media/3.png?raw=true" width="45%"></img>
## Prerequisites

- Python 3.x
- Pygame library
- NumPy library

## Getting Started

Clone the repository:

```bash
git clone https://github.com/SMollov/Slime-Mold-Simulation.git
```
    
Install the required dependencies:

```bash
pip3 install pygame numpy
```

Run the script:

```bash
python3 slime.py
```

## Usage

1. Press Start.

2. Draw Barriers. Left-click to draw on    the grid line by line. Right-click to toggle drawing mode on/off.

3. Press Continue.

4. Left-click to select start and end points.

5. The algorithm will display the simulation, and the optimal path between the selected points. The steps can be repeated after the search is done.


## License

[MIT](https://choosealicense.com/licenses/mit/)


## Contributing

If you have any suggestions, improvements, or bug fixes, please feel free to submit a pull request.
