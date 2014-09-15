project(hybrid)

set(hybrid_SRC
    ${CMAKE_CURRENT_BINARY_DIR}/hybrid/hybrid_module_wrapper.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/hybrid/mainwindow_wrapper.cpp
)

set(hybrid_INCLUDE_DIRECTORIES
    ${SHIBOKEN_INCLUDE_DIR}
    ${PYTHON_INCLUDE_PATH}
    ${PYSIDE_INCLUDE_DIR}
    ${PYSIDE_INCLUDE_DIR}/QtCore
    ${PYSIDE_INCLUDE_DIR}/QtGui
    ${QT_INCLUDE_DIR}
    ${QT_QTCORE_INCLUDE_DIR}
    ${QT_QTGUI_INCLUDE_DIR}
    ${LIBHYBRID_DIR}
)

set(hybrid_LINK_LIBRARIES
    ${SHIBOKEN_PYTHON_LIBRARIES}
    ${SHIBOKEN_LIBRARY}
    ${QT_QTCORE_LIBRARY}
    ${QT_QTGUI_LIBRARY}
    ${PYSIDE_LIBRARY}
    ${LIBHYBRID_DIR}/libhybrid.so
)

include_directories(hybrid ${hybrid_INCLUDE_DIRECTORIES})
add_library(hybrid MODULE ${hybrid_SRC})
set_property(TARGET hybrid PROPERTY PREFIX "")
target_link_libraries(hybrid ${hybrid_LINK_LIBRARIES})

add_custom_command(OUTPUT ${hybrid_SRC}
                   COMMAND ${GENERATOR}
                   --generatorSet=shiboken --enable-parent-ctor-heuristic --enable-pyside-extensions --enable-return-value-heuristic
                   ${CMAKE_SOURCE_DIR}/hybrid/global.h
                   --include-paths=${QT_INCLUDE_DIR}:${LIBHYBRID_DIR}
                   --typesystem-paths=${typesystem_path}:{PYSIDE_TYPESYSTEMS}:/usr/local/share/PySide/typesystems
                   --output-directory=${CMAKE_CURRENT_BINARY_DIR}
                   ${CMAKE_CURRENT_SOURCE_DIR}/typesystem_hybrid.xml
                   WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                   COMMENT "Running generator for libhybrid..."
                  )
