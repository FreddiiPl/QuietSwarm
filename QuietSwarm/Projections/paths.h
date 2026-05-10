#ifndef PATHS_H
#define PATHS_H

#include <stddef.h>

int get_executable_directory(char *output_path, size_t max_size);
void getAbsolutePath(char *output_buffer, size_t max_size, const char *relpath);

#endif