"""
Gray-Scott Reaction-Diffusion Simulation
Main entry point using moderngl-window
"""

import moderngl_window as mglw
import numpy as np
from imgui_bundle import imgui

from gray_scott import GrayScottSimulation, GrayScottRenderer


class GrayScottWindow(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Gray-Scott Reaction-Diffusion"
    window_size = (800, 800)
    aspect_ratio = 1.0
    resizable = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.simulation = GrayScottSimulation(width=128, height=128)
        
        self.renderer = GrayScottRenderer(
            self.ctx, 
            self.simulation.width, 
            self.simulation.height
        )
        
        # Track mouse state
        self.mouse_down = False
        self.mouse_pos = (0, 0)
        
        # Create imgui context
        imgui.create_context()
        
        # Configure imgui IO
        io = imgui.get_io()
        io.display_size = self.window_size
        
        # Initialize OpenGL3 renderer (this builds the font atlas)
        imgui.backends.opengl3_init("#version 330")
    
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
        
        # Render imgui
        self._render_gui()
    
    def _render_gui(self):
        """Render the imgui configuration window"""
        imgui.backends.opengl3_new_frame()
        imgui.new_frame()
        
        imgui.begin("Gray-Scott Parameters")
        
        # Feed rate slider
        changed, self.simulation.f = imgui.slider_float("Feed Rate (f)", self.simulation.f, 0.0, 0.1)
        
        # Kill rate slider
        changed, self.simulation.k = imgui.slider_float("Kill Rate (k)", self.simulation.k, 0.0, 0.1)
        
        # Time step slider
        changed, self.simulation.dt = imgui.slider_float("Time Step (dt)", self.simulation.dt, 0.1, 2.0)
        
        # Steps per frame slider
        changed, self.simulation.steps_per_frame = imgui.slider_int("Steps per Frame", self.simulation.steps_per_frame, 1, 20)
        
        # Diffusion rate U slider
        changed, self.simulation.Du = imgui.slider_float("Diffusion U (Du)", self.simulation.Du, 0.01, 0.5)
        
        # Diffusion rate V slider
        changed, self.simulation.Dv = imgui.slider_float("Diffusion V (Dv)", self.simulation.Dv, 0.01, 0.5)
        
        imgui.end()
        
        imgui.render()
        imgui.backends.opengl3_render_draw_data(imgui.get_draw_data())
    
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
