# 3D Rubik's Cube Simulator

A fully interactive 3D Rubik's Cube built with Python using **Pygame** and **PyOpenGL**.

You can freely rotate the entire cube by dragging with your mouse to see different sides. You can also rotate each layer of the cube using keyboard shortcuts with smooth animations — just like a real Rubik's Cube!

## Features

-   Realistic 3D rendering with classic colors and black edges
-   Mouse drag to rotate and view the cube from any angle
-   Animated 90° layer rotations
-   Shift key to reverse rotation direction
-   Single-file, clean implementation

## Installation & Running

### Requirements

-   Python 3.6 or higher

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/amirsafa2024/Visual-Rubik-s-Cube.git
    cd THE-REPO-DIRECTORY
    ```

2. (Recommended) Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate        # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the simulator:
    ```bash
    python rubikCube.py
    ```

## Controls

### Viewing the Cube

-   **Left-click and drag** with the mouse to rotate the whole cube and see different sides.

### Rotating Layers

Press these keys to rotate the corresponding face **counter-clockwise**:

-   `U` → Up face (white)
-   `D` → Down face (yellow)
-   `F` → Front face (green)
-   `B` → Back face (blue)
-   `L` → Left face (orange)
-   `R` → Right face (red)

Hold **Shift** while pressing any of the above keys to rotate the face **clockwise** instead.

-   `Esc` → Quit the program

## Credits

Made with ❤️ using Pygame and PyOpenGL.  
Window title inspiration: "Dish Dirin Dirin Mashallah xD"

---

Have fun scrambling and solving the cube! Feel free to open issues or submit pull requests if you find bugs or want to add features. 🎲
