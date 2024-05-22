#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>

#define FILE_SIZE (128L * 1024 * 1024 * 1024) // 16 GB
#define BUFFER_SIZE (1024 * 1024)           // 1 MB
#define ALIGN_SIZE (4096)                   // 4 KB alignment for direct I/O

int main() {
    int fd;
    void *buffer;
    ssize_t written;
    struct timespec start, end;
    double duration;

    // Allocate aligned memory for direct I/O
    if (posix_memalign(&buffer, ALIGN_SIZE, BUFFER_SIZE) != 0) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    // Fill the buffer with random data
    for (size_t i = 0; i < BUFFER_SIZE; ++i) {
        ((char*)buffer)[i] = rand() % 256;
    }

    // Open a file for writing with direct I/O
    fd = open("test_file.dat", O_WRONLY | O_CREAT | O_TRUNC | O_DIRECT, 0644);
    if (fd == -1) {
        perror("File opening failed");
        free(buffer);
        return 1;
    }

    // Start the high-resolution timer
    if (clock_gettime(CLOCK_MONOTONIC, &start) == -1) {
        perror("clock_gettime start failed");
        close(fd);
        free(buffer);
        return 1;
    }

    // Write 16 GB to the file
    for (size_t i = 0; i < FILE_SIZE / BUFFER_SIZE; ++i) {
        written = write(fd, buffer, BUFFER_SIZE);
        if (written != BUFFER_SIZE) {
            perror("File write failed");
            close(fd);
            free(buffer);
            return 1;
        }
    }

    // Ensure all data is flushed to disk
    if (fsync(fd) == -1) {
        perror("fsync failed");
        close(fd);
        free(buffer);
        return 1;
    }

    // Stop the high-resolution timer
    if (clock_gettime(CLOCK_MONOTONIC, &end) == -1) {
        perror("clock_gettime end failed");
        close(fd);
        free(buffer);
        return 1;
    }

    // Calculate the duration in seconds
    duration = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1E9;

    // Close the file
    close(fd);

    // Delete the file
    if (remove("test_file.dat") != 0) {
        perror("File deletion failed");
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
