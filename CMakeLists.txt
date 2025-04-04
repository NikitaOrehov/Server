cmake_minimum_required(VERSION 3.10)
project(heroku-cpp-server)

set(CMAKE_CXX_STANDARD 14)

add_executable(heroku-cpp-server main.cpp)

# ”станавливаем директорию дл€ бинарника (чтобы Heroku его нашел)
set_target_properties(heroku-cpp-server PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

#  опируем бинарник в корень проекта
install(TARGETS heroku-cpp-server DESTINATION .)