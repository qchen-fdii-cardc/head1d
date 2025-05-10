cmake_minimum_required(VERSION 3.10)
project(heat1d_solver VERSION 1.0)

# Set C++ standard to C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Find Eigen3
find_package(Eigen3 3.3 REQUIRED CONFIG)
if(NOT Eigen3_FOUND)
    message(FATAL_ERROR "Eigen3 not found. Please install Eigen3 and ensure it is in your CMAKE_PREFIX_PATH.")
else()
    message(STATUS "Found Eigen3: ${Eigen3_INCLUDE_DIRS}")
endif()

# Add executable
add_executable(heat1d_solver ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp)

# Link Eigen3 to the executable
target_include_directories(heat1d_solver PUBLIC ${Eigen3_INCLUDE_DIRS})

# Optional: Add compiler flags for optimization or debugging
# target_compile_options(heat1d_solver PRIVATE -O3) # Example for optimization
# target_compile_options(heat1d_solver PRIVATE -g)   # Example for debugging

# Include directories
target_include_directories(heat1d_solver PRIVATE include)

# Set output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

# install(TARGETS heat1d_solver DESTINATION bin) 