#version 410 core

in float vEnergy;
out vec4 FragColor;

void main() {

    if (vEnergy < -0.5) {
        FragColor = vec4(0.3, 0.3, 0.3, 1.0);
        return;
    }

    float r = smoothstep(0.3, 0.7, vEnergy);
    float g = smoothstep(0.0, 0.4, vEnergy) - smoothstep(0.6, 1.0, vEnergy);
    float b = 1.0 - smoothstep(0.2, 0.6, vEnergy);

    FragColor = vec4(r, g, b, 1.0);
}