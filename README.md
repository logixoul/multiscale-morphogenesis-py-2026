# Gray-Scott Reaction-Diffusion Simulation

A real-time Gray-Scott reaction-diffusion simulation using Arrayfire for GPU-accelerated computation and ModernGL for visualization.

## ⚠️ ArrayFire Installation Required

**Important**: This project requires the ArrayFire system library to be installed. The Python package alone is not sufficient.

### Windows Installation

1. Download the ArrayFire installer from https://arrayfire.com/download/
2. Run the installer and follow the instructions
3. Add ArrayFire to your system PATH (usually `C:\Program Files\ArrayFire\v3\bin`)
4. Restart your terminal/Python environment

### Verify Installation

After installing ArrayFire, verify it works:
```bash
python -c "import arrayfire; print('ArrayFire loaded successfully')"
```

## Running the Simulation

Once ArrayFire is installed:

```bash
python main.py
```

## Controls

- **Left Mouse Click/Drag**: Add chemicals at the cursor position
- **Close Window**: Exit the simulation

## Default Parameters

- Resolution: 512x512
- Feed rate (f): 0.055
- Kill rate (k): 0.062
- Diffusion rate U: 1.0
- Diffusion rate V: 0.5
- Simulation steps per frame: 8

## Project Structure

```
gray_scott_simulation/
├── requirements.txt      # Python dependencies
├── main.py              # Main entry point
└── gray_scott/
    ├── __init__.py      # Package initialization
    ├── simulation.py   # Gray-Scott simulation logic
    └── renderer.py     # ModernGL renderer
```

## Future Enhancements

- Integration with imgui-bundle for parameter controls
- Additional preset patterns
- Multiple color schemes
- Save/load functionality
