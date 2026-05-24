cmake_minimum_required(VERSION 3.12)
project(OrbitVisualizerCore)

set(CMAKE_CXX_STANDARD 17)

# Locate Pybind11 and system libraries
find_package(pybind11 REQUIRED)
find_package(GLEW REQUIRED)
find_package(GLFW3 REQUIRED)
find_package(OpenGL REQUIRED)

# Use pybind11_add_module instead of add_executable
pybind11_add_module(orbit_plotter main.cpp)

target_link_libraries(orbit_plotter PRIVATE 
    GLEW::GLEW 
    glfw 
    OpenGL::GL
)