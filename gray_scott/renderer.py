"""
Gray-Scott Reaction-Diffusion Renderer using ModernGL
"""

import moderngl
import numpy as np


class GrayScottRenderer:
    def __init__(self, ctx, width, height):
        self.ctx = ctx
        self.width = width
        self.height = height
        
        # Create texture for the simulation
        self.texture = self.ctx.texture((width, height), 1, dtype='f4')
        
        # Create shader program
        self._create_shaders()
        
        # Create fullscreen quad
        self._create_quad()
    
    def _create_shaders(self):
        """Create shader program for rendering"""
        # Vertex shader - simple pass-through
        vertex_shader = """
        #version 330
        
        in vec2 in_vert;
        in vec2 in_uv;
        
        out vec2 v_uv;
        
        void main() {
            gl_Position = vec4(in_vert, 0.0, 1.0);
            v_uv = in_uv;
        }
        """
        
        # Fragment shader - color mapping
        fragment_shader = """
        #version 330
        
        uniform sampler2D u_texture;
        
        in vec2 v_uv;
        
        out vec4 f_color;
        
        // Simple color mapping for V concentration
        vec3 color_map(float v) {
            // Color scheme: dark blue -> cyan -> white
            vec3 c1 = vec3(0.0, 0.0, 0.1);   // Dark blue background
            vec3 c2 = vec3(0.0, 0.5, 0.8);   // Cyan
            vec3 c3 = vec3(1.0, 1.0, 1.0);   // White
            
            if (v < 0.5) {
                return mix(c1, c2, v * 2.0);
            } else {
                return mix(c2, c3, (v - 0.5) * 2.0);
            }
        }
        
        void main() {
            float v = texture(u_texture, v_uv).r;
            float fw = fwidth(v);
            v = smoothstep(0.25 - fw * 0.5, 0.25 + fw * 0.5, v); // Anti-aliasing
            vec3 color = color_map(v);
            f_color = vec4(color, 1.0);
        }
        """
        
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
    
    def _create_quad(self):
        """Create a fullscreen quad for rendering"""
        # Vertex data: position (x, y) and UV coordinates (u, v)
        vertices = np.array([
            # position    # UV
            -1.0, -1.0,   0.0, 0.0,
             1.0, -1.0,   1.0, 0.0,
            -1.0,  1.0,   0.0, 1.0,
             1.0,  1.0,   1.0, 1.0,
        ], dtype='f4')
        
        # Create buffer
        self.vbo = self.ctx.buffer(vertices)
        
        # Create vertex array
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, '2f 2f', 'in_vert', 'in_uv'),
            ],
        )
    
    def render(self, texture_data):
        """Render the simulation texture to screen"""
        # Update texture with new data
        self.texture.write(texture_data)
        
        # Bind texture
        self.texture.use(location=0)
        
        # Render quad
        self.vao.render(moderngl.TRIANGLE_STRIP)
    
    def release(self):
        """Release resources"""
        self.vbo.release()
        self.vao.release()
        self.texture.release()
        self.program.release()
