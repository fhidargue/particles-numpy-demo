#version 410 core

layout(location = 0) out vec4 fragment_color;
in vec3 out_color;
void main()
{
    fragment_color.rgb = out_color;
}
