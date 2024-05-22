#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define FILE_SIZE (1L * 1024 * 1024 * 1024) // 1 GB
#define BUFFER_SIZE (1024 * 1024)           // 1 MB

int main() {
    FILE *file;
    char *buffer;
    size_t written;
    clock_t start, end;
    double duration;

    // Allocate 1 MB buffer
    buffer = (char *)malloc(BUFFER_SIZE);
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    // Fill the buffer with random data
    for (size_t i = 0; i < BUFFER_SIZE; ++i) {
        buffer[i] = rand() % 256;
    }

    // Open a file for writing
    file = fopen("test_file.dat", "wb");
    if (file == NULL) {
        fprintf(stderr, "File opening failed\n");
        free(buffer);
        return 1;
    }

    // Start the timer
    start = clock();

    // Write 1 GB to the file
    for (size_t i = 0; i < FILE_SIZE / BUFFER_SIZE; ++i) {
        written = fwrite(buffer, 1, BUFFER_SIZE, file);
        if (written != BUFFER_SIZE) {
            fprintf(stderr, "File write failed\n");
            fclose(file);
            free(buffer);
            return 1;
        }
    }

    // Stop the timer
    end = clock();
    duration = (double)(end - start) / CLOCKS_PER_SEC;

    // Close the file
    fclose(file);

    // Delete the file
    if (remove("test_file.dat") != 0) {
        fprintf(stderr, "File deletion failed\n");
        free(buffer);
        return 1;
    }

    // Free the buffer
    free(buffer);

    // Calculate and print the write speed
    double write_speed = (double)FILE_SIZE / (1024 * 1024) / duration; // MB/s
    printf("Write speed: %.2f MB/s\n", write_speed);

    return 0;
}
