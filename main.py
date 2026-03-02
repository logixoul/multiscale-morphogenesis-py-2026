"""
Gray-Scott Reaction-Diffusion Simulation
Main entry point using moderngl-window
"""

import moderngl_window as mglw
import numpy as np

from gray_scott import GrayScottSimulation, GrayScottRenderer

class GrayScottWindow(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Gray-Scott Reaction-Diffusion"
    window_size = (800, 800)
    aspect_ratio = 1.0
    resizable = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.simulation = GrayScottSimulation(width=256, height=256)
        
        self.renderer = GrayScottRenderer(
            self.ctx, 
            self.simulation.width, 
            self.simulation.height
        )
        
        # Track mouse state
        self.mouse_down = False
        self.mouse_pos = (0, 0)
    
    def on_render(self, time, frame_time):
        # Handle mouse input
        if self.mouse_down:
            # Convert screen coordinates to normalized (0-1)
            x = self.mouse_pos[0] / self.window_size[0]
            y = 1.0 - self.mouse_pos[1] / self.window_size[1]  # Flip Y for texture coords
            self.simulation.add_chemical(x, y, radius=15)
        
        self.simulation.update()
        
        texture_data = self.simulation.get_texture_array()
        
        self.renderer.render(texture_data)
    
    def on_mouse_press_event(self, x, y, button):
        if button == self.wnd.mouse.left:
            self.mouse_down = True
            self.mouse_pos = (x, y)
            # Add initial chemical on click
            norm_x = x / self.window_size[0]
            norm_y = 1.0 - y / self.window_size[1]  # Flip Y for texture coords
            self.simulation.add_chemical(norm_x, norm_y, radius=15)
    
    def on_mouse_release_event(self, x, y, button):
        if button == self.wnd.mouse.left:
            self.mouse_down = False
    
    def on_mouse_drag_event(self, x, y, dx, dy):
        self.mouse_pos = (x, y)
    
    def on_mouse_move_event(self, x, y, dx, dy):
        if self.mouse_down:
            self.mouse_pos = (x, y)
    
    def on_close(self):
        self.renderer.release()
        super().on_close()


if __name__ == '__main__':
    mglw.run_window_config(GrayScottWindow)
