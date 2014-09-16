project(hybridbinding)

cmake_minimum_required(VERSION 2.6)
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/Macros/
                      ${CMAKE_MODULE_PATH}
                      /usr/share/cmake-2.8/Modules)

set(QT_INCLUDE_DIR /usr/local/Trolltech/Qt-4.8.1/include)
set(SHIBOKEN_INCLUDE_DIR /usr/local/lib/python2.7/dist-packages/PySide-1.2.1-py2.7.egg/PySide/include/shiboken)

find_package(PythonLibs REQUIRED)
find_package(PySide REQUIRED)

set(LIBHYBRID_DIR ${CMAKE_SOURCE_DIR}/../libhybrid)

find_program(GENERATOR generatorrunner REQUIRED)
if (NOT GENERATOR)
    message(FATAL_ERROR "You need to specify GENERATOR variable (-DGENERATOR=value)")
endif()

if(CMAKE_HOST_UNIX)
    option(ENABLE_GCC_OPTIMIZATION "Enable specific GCC flags to optimization library size and performance. Only available on Release Mode" 0)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fvisibility=hidden -Wno-strict-aliasing")
    set(CMAKE_CXX_FLAGS_DEBUG "-g")
    if(ENABLE_GCC_OPTIMIZATION)
        set(CMAKE_BUILD_TYPE Release)
        set(CMAKE_CXX_FLAGS_RELEASE "-DNDEBUG -Os -Wl,-O1")
        if(NOT CMAKE_HOST_APPLE)
            set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,--hash-style=gnu")
        endif()
    endif()
 
    if(CMAKE_HOST_APPLE)
        if (NOT QT_INCLUDE_DIR)
            set(QT_INCLUDE_DIR "/Library/Frameworks")
         endif()
    endif()
endif()
 

add_subdirectory(hybrid)
