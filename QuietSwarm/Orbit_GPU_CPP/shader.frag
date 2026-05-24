#version 410 core

in float vEnergy;
out vec4 FragColor;

void main() {
    float r = smoothstep(0.3, 0.7, vEnergy);
    float g = smoothstep(0.0, 0.4, vEnergy) - smoothstep(0.6, 1.0, vEnergy);
    float b = 1.0 - smoothstep(0.2, 0.6, vEnergy);

    FragColor = vec4(r, g, b, 1.0);
}