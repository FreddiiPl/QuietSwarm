
#define GL_SILENCE_DEPRECATION
#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <fstream>   // FIX: Krävs för std::ifstream
#include <sstream>   // FIX: Krävs för std::stringstream
#include <stdexcept> // FIX: Krävs för std::runtime_error

namespace py = pybind11;


struct GPUParticle {
    float x, y, z, energy;
};

// Globala variabler för enkel kamerastyrning
float camYaw = 0.78f;  // Startvinkel (45 grader)
float camPitch = 0.5f; // Startlutning
float camRadius = 15.0f; 

void key_callback(GLFWwindow* window, int key, int scancode, int action, int mods) {
    if (action == GLFW_PRESS || action == GLFW_REPEAT) {
        if (key == GLFW_KEY_LEFT || key == GLFW_KEY_A)  camYaw -= 0.1f;
        if (key == GLFW_KEY_RIGHT || key == GLFW_KEY_D) camYaw += 0.1f;
        if (key == GLFW_KEY_UP || key == GLFW_KEY_W)    camRadius -= 1.0f; // Zooma in
        if (key == GLFW_KEY_DOWN || key == GLFW_KEY_S)  camRadius += 1.0f; // Zooma ut
        if (key == GLFW_KEY_R) camPitch += 0.05f;
        if (key == GLFW_KEY_F) camPitch -= 0.05f;
    }
}


GLFWwindow* initializeWindow(float width, float height) {

    if (!glfwInit()) return nullptr;

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 1);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);   

    GLFWwindow* window = glfwCreateWindow(width, height, "Orbital states", nullptr, nullptr);

    if (!window) { glfwTerminate(); return nullptr; }
    glfwMakeContextCurrent(window);
    glfwSetKeyCallback(window, key_callback);

    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) { glfwTerminate(); return nullptr; }

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_PROGRAM_POINT_SIZE);

    return window;
}


std::string readShaderFile(const std::string& path) {
    std::ifstream file(path);

    if (!file.is_open()) {
        throw std::runtime_error("Failed to open shader:" + path);
    }

    std::stringstream buffer;
    buffer << file.rdbuf();

    return buffer.str();
}


unsigned int initializeShaders(const char* vertexShaderSource,
                               const char* fragmentShaderSource
                            ) {

    unsigned int vs = glCreateShader(GL_VERTEX_SHADER); 
    glShaderSource(vs, 1, &vertexShaderSource, NULL); 
    glCompileShader(vs);

    unsigned int fs = glCreateShader(GL_FRAGMENT_SHADER); 
    glShaderSource(fs, 1, &fragmentShaderSource, NULL); 
    glCompileShader(fs);

    unsigned int program = glCreateProgram(); 
    glAttachShader(program, vs); 
    glAttachShader(program, fs); 
    glLinkProgram(program);

    glDeleteShader(vs); glDeleteShader(fs);

    return program;
}


std::pair<std::vector<GPUParticle>, std::vector<float>> correctScaling(const std::vector<float>& x, 
                                                    const std::vector<float>& y, 
                                                    const std::vector<float>& z,
                                                    const std::vector<float>& energy) {

    float a_normalize = 6378136.6f;
    // Because normalize in respect of wgs84 sma
    float minX = x[0] / a_normalize, maxX = minX;
    float minY = y[0] / a_normalize, maxY = minY;
    float minZ = z[0] / a_normalize, maxZ = minZ;
    
    std::vector<GPUParticle> gpuData(x.size());

    for (size_t i = 0; i < x.size(); ++i) {
        gpuData[i].x = x[i] / a_normalize;
        gpuData[i].y = y[i] / a_normalize;
        gpuData[i].z = z[i] / a_normalize;
        gpuData[i].energy = energy[i];

        minX = std::min(minX, gpuData[i].x); maxX = std::max(maxX, gpuData[i].x);
        minY = std::min(minY, gpuData[i].y); maxY = std::max(maxY, gpuData[i].y);
        minZ = std::min(minZ, gpuData[i].z); maxZ = std::max(maxZ, gpuData[i].z);
    }

    float centerX = (minX + maxX) / 2.0f;
    float centerY = (minY + maxY) / 2.0f;
    float centerZ = (minZ + maxZ) / 2.0f;

    
    float maxDelta = std::max({maxX - minX, maxY - minY, maxZ - minZ});
    camRadius = maxDelta * 2.0f; 
    if (camRadius < 1.0f) camRadius = 5.0f; 
    
    std::vector<float> scalingMetrics = {centerX,
                                centerY,
                                centerZ,
                                maxDelta,
                                camRadius};

    return std::make_pair(gpuData, scalingMetrics);
}


std::pair<unsigned int, unsigned int> initializeVertexObjects(const std::vector<GPUParticle>& gpuData) {
    unsigned int VAO, VBO;

    glGenVertexArrays(1, &VAO); 
    glGenBuffers(1, &VBO);

    glBindVertexArray(VAO); 
    glBindBuffer(GL_ARRAY_BUFFER, VBO);

    glBufferData(GL_ARRAY_BUFFER, gpuData.size() * sizeof(GPUParticle), gpuData.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(GPUParticle), (void*)0); glEnableVertexAttribArray(0);
    glVertexAttribPointer(1, 1, GL_FLOAT, GL_FALSE, sizeof(GPUParticle), (void*)(sizeof(float) * 3)); glEnableVertexAttribArray(1);

    return std::make_pair(VAO, VBO);
}


void launch_opengl_plotter(const std::vector<float>& x, 
                           const std::vector<float>& y, 
                           const std::vector<float>& z, 
                           const std::vector<float>& energy,
                           const std::string& vertPath,
                           const std::string& fragPath) {

    float width = 1200; 
    float height = 800;
    GLFWwindow* window   = initializeWindow(width, height);

    std::string vertCode = readShaderFile(vertPath);
    std::string fragCode = readShaderFile(fragPath);

    const char* vertSource = vertCode.c_str();
    const char* fragSource = fragCode.c_str();
    unsigned int program = initializeShaders(vertSource, fragSource);

    auto [particles, metrics] = correctScaling(x, y, z, energy);

    auto [VAO, VBO] = initializeVertexObjects(particles);
    

    float centerX   = metrics[0];
    float centerY   = metrics[1];
    float centerZ   = metrics[2];
    float maxDelta  = metrics[3];
    camRadius = metrics[4];
    while (!glfwWindowShouldClose(window)) {
        glClearColor(0.05f, 0.05f, 0.05f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glUseProgram(program);

        float fov_rad = 45.0f * M_PI / 180.0f; // 45 degrees in rad
        float aspect = width / height;
        float f = 1.0f / tan(fov_rad / 2.0f); // focal point ??
        

        float farPlane = camRadius * 10.0f;
        float nearPlane = 0.1f;

        float projMatrix[] = {f/aspect, 0, 0, 0, 
                              0, f, 0, 0, 
                              0, 0, (farPlane+nearPlane)/(nearPlane-farPlane), -1, 
                              0, 0, (2.0f*farPlane*nearPlane)/(nearPlane-farPlane), 0
                            };

        // Camera position
        float camX = centerX + camRadius * cos(camPitch) * sin(camYaw);
        float camY = centerY + camRadius * sin(camPitch);
        float camZ = centerZ + camRadius * cos(camPitch) * cos(camYaw);

        // View matrix
        float zx = camX - centerX, zy = camY - centerY, zz = camZ - centerZ; 
        float len = sqrt(zx*zx + zy*zy + zz*zz); zx/=len; zy/=len; zz/=len;
        float rx = -zz, ry = 0, rz = zx; float rlen = sqrt(rx*rx + rz*rz); rx/=rlen; rz/=rlen;
        float ux = -zy*rz, uy = zx*rz - zz*rx, uz = zy*rx;
        
        float viewMatrix[] = {rx, ux, zx, 0, 
                              ry, uy, zy, 0, 
                              rz, uz, zz, 0, 
                              -(rx*camX+ry*camY+rz*camZ), -(ux*camX+uy*camY+uz*camZ), -(zx*camX+zy*camY+zz*camZ), 1
                            };

        glUniformMatrix4fv(glGetUniformLocation(program, "projection"), 1, GL_FALSE, projMatrix);
        glUniformMatrix4fv(glGetUniformLocation(program, "view"), 1, GL_FALSE, viewMatrix);

        glBindVertexArray(VAO);
        glDrawArrays(GL_POINTS, 0, static_cast<GLsizei>(particles.size()));

        glfwSwapBuffers(window); glfwPollEvents();
    }

    glDeleteVertexArrays(1, &VAO); 
    glDeleteBuffers(1, &VBO); 
    glDeleteProgram(program);
    glfwDestroyWindow(window); 
    glfwTerminate();
}

PYBIND11_MODULE(orbit_plotter, m) {
    m.def("plot_ecef", &launch_opengl_plotter, "A function that displays ECEF points inside native OpenGL pipelines.");
}
