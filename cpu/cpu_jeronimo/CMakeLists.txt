cmake_minimum_required(VERSION 3.5)
project(kmeans_c)

set(CMAKE_CXX_STANDARD 11)

#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")

set(SOURCE_FILES main.cpp)
add_executable(kmeans_c ${SOURCE_FILES})
