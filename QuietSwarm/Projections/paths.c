#include "paths.h"
#include <stdio.h>
#include <unistd.h>
#include <limits.h>
#include <string.h>




int get_executable_directory(char *output_path, size_t max_size) {
    char executable_path[PATH_MAX];
    memset(executable_path, 0, sizeof(executable_path));

    strncpy(executable_path, __FILE__, sizeof(executable_path) - 1);
    executable_path[sizeof(executable_path) - 1] = '\0';

    char *last_slash = strrchr(executable_path, '/');
    if (last_slash != NULL) {
        *last_slash = '\0';
    } else {
        strncpy(executable_path, ".", sizeof(executable_path) - 1);
    }

    int written = snprintf(output_path, max_size, "%s", executable_path);
    return (written > 0 && written < (int)max_size);

}


void getAbsolutePath(char *output_buffer, size_t max_size, const char *relpath) {
    char base_directory[PATH_MAX];
    base_directory[sizeof(base_directory) - 1] = '\0';

    if (!get_executable_directory(base_directory, sizeof(base_directory))) {
        fprintf(stderr, "Critical security error: could not determine file path!\n");
        return;
    }

    int written = snprintf(output_buffer, max_size, "%s/%s", base_directory, relpath);

    if (written >= (int)max_size || written < 0) {
        fprintf(stderr, "Error: Search path to long for buffer.\n");
        if (max_size > 0) output_buffer[0] = '\0'; 
        return;
    }
}