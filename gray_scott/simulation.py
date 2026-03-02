"""
Gray-Scott Reaction-Diffusion Simulation using Arrayfire
"""

import arrayfire as af
import numpy as np


class GrayScottSimulation:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        
        # Gray-Scott parameters
        self.f = 0.055  # feed rate
        self.k = 0.062  # kill rate
        self.dt = 1.0   # time step
        self.steps_per_frame = 8
        
        # Diffusion rates
        self.Du = 1.0
        self.Dv = 0.5
        
        # Initialize concentrations
        self.U = af.constant(1.0, width, height, dtype=af.Dtype.f32)
        self.V = af.constant(0.0, width, height, dtype=af.Dtype.f32)
        
        # Initialize with some seed pattern
        self._seed_pattern()
    
    def _seed_pattern(self):
        """Seed the simulation with an initial pattern"""
        # Create a square of V in the center
        center_x = self.width // 2
        center_y = self.height // 2
        radius = 20
        
        # Create coordinate grids
        x = af.range(self.width)
        y = af.range(self.height)
        
        # Use broadcasting to create a circular mask
        x_broadcast = af.reorder(x, 0, 1)  # Shape: (width, 1)
        y_broadcast = af.reorder(y, 1, 0)  # Shape: (1, height)
        
        # Calculate distance from center
        dx = x_broadcast - center_x
        dy = y_broadcast - center_y
        distance = af.sqrt(dx * dx + dy * dy)
        
        # Create mask for circle
        mask = distance < radius
        
        # Apply seed: set V to 1.0 in the circle
        self.V = af.select(mask, 1.0, self.V)
        
        # Also add a few random spots
        np.random.seed(42)
        for _ in range(10):
            rx = np.random.randint(self.width // 4, 3 * self.width // 4)
            ry = np.random.randint(self.height // 4, 3 * self.height // 4)
            r = np.random.randint(5, 15)
            
            dx = x_broadcast - rx
            dy = y_broadcast - ry
            distance = af.sqrt(dx * dx + dy * dy)
            circle_mask = distance < r
            
            self.V = af.select(circle_mask, 1.0, self.V)
    
    def _laplacian(self, arr):
        """Compute Laplacian using 3x3 convolution kernel"""
        # 3x3 Laplacian kernel (with center weight -4 and neighbors -1)
        # Using Arrayfire's shift for neighbor sampling
        
        # Get neighbors (up, down, left, right, and diagonals)
        left = af.shift(arr, 1, 0)
        right = af.shift(arr, -1, 0)
        up = af.shift(arr, 0, 1)
        down = af.shift(arr, 0, -1)
        
        # Diagonals
        up_left = af.shift(arr, 1, 1)
        up_right = af.shift(arr, -1, 1)
        down_left = af.shift(arr, 1, -1)
        down_right = af.shift(arr, -1, -1)
        
        # Center weight: -4, neighbors: 1 (standard 5-point stencil + 4 diagonals)
        # Using simplified 5-point stencil for better performance
        laplacian = (left + right + up + down - 4 * arr)
        
        return laplacian
    
    def step(self):
        """Perform one simulation step"""
        # Compute Laplacians
        lapU = self._laplacian(self.U)
        lapV = self._laplacian(self.V)
        
        # Gray-Scott reaction-diffusion equations
        # dU/dt = Du * lapU - U*V^2 + f*(1-U)
        # dV/dt = Dv * lapV + U*V^2 - (f+k)*V
        
        # Compute reaction term
        reaction = self.U * self.V * self.V
        
        # Update concentrations
        dU = self.Du * lapU - reaction + self.f * (1.0 - self.U)
        dV = self.Dv * lapV + reaction - (self.f + self.k) * self.V
        
        self.U = self.U + self.dt * dU
        self.V = self.V + self.dt * dV
        
        # Clamp values to prevent instability
        self.U = af.clamp(self.U, 0.0, 1.0)
        self.V = af.clamp(self.V, 0.0, 1.0)
    
    def update(self):
        """Run multiple simulation steps per frame"""
        for _ in range(self.steps_per_frame):
            self.step()
    
    def add_chemical(self, x, y, radius=10):
        """Add chemicals at the specified position"""
        # Convert to integer coordinates
        cx = int(x * self.width)
        cy = int(y * self.height)
        
        # Clamp to valid range
        cx = max(0, min(self.width - 1, cx))
        cy = max(0, min(self.height - 1, cy))
        
        # Create coordinate grids
        x_vals = af.range(self.width)
        y_vals = af.range(self.height)
        
        x_broadcast = af.reorder(x_vals, 0, 1)
        y_broadcast = af.reorder(y_vals, 1, 0)
        
        # Calculate distance from click point
        dx = x_broadcast - cx
        dy = y_broadcast - cy
        distance = af.sqrt(dx * dx + dy * dy)
        
        # Create circular mask
        mask = distance < radius
        
        # Add V chemical at the location
        self.V = af.select(mask, 1.0, self.V)
    
    def get_texture_data(self):
        """Get the V concentration as numpy array for texture"""
        # Convert to numpy and return
        return self.V.to_ndarray()
    
    def get_texture_array(self):
        """Get the V concentration as a contiguous array for texture"""
        v_data = self.V.to_ndarray()
        # Ensure correct shape and dtype
        return np.ascontiguousarray(v_data.astype(np.float32))
