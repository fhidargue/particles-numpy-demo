#version 410 core

layout(location = 0) out vec4 fragment_color;
in vec3 out_color;
void main()
{
    vec2 circle_coord = 2.0 * gl_PointCoord - 1.0;
    if (dot(circle_coord, circle_coord) > 1.0) {
        discard;
    }

    fragment_color.rgb = out_color;
}
