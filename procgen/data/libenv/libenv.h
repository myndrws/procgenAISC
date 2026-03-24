/*
 * libenv.h - Interface for procedurally generated environments
 * This header defines the C API for libenv-compatible environments
 * Compatible with OpenAI gym3 libenv interface
 */

#ifndef LIBENV_H
#define LIBENV_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// Version
#define LIBENV_VERSION 1

// Platform-specific export macros
#if defined(_WIN32) || defined(_WIN64)
    #ifdef LIBENV_EXPORTS
        #define LIBENV_API __declspec(dllexport)
    #else
        #define LIBENV_API __declspec(dllimport)
    #endif
#else
    #define LIBENV_API __attribute__((visibility("default")))
#endif

// Data types
enum libenv_dtype {
    LIBENV_DTYPE_UINT8 = 1,
    LIBENV_DTYPE_INT32 = 2,
    LIBENV_DTYPE_FLOAT32 = 3
};

// Scalar types
#define LIBENV_SCALAR_TYPE_DISCRETE 2
#define LIBENV_SCALAR_TYPE_BOX 3

// Space names
enum libenv_space_name {
    LIBENV_SPACE_OBSERVATION = 0,
    LIBENV_SPACE_ACTION = 1,
    LIBENV_SPACE_INFO = 2
};

// Value union
union libenv_value {
    uint8_t uint8;
    int32_t int32;
    float float32;
};

// Tensor type description
struct libenv_tensortype {
    char name[256];     // name of the tensor
    int scalar_type;    // LIBENV_SCALAR_TYPE_*
    int dtype;          // libenv_dtype
    int ndim;           // number of dimensions
    int *shape;         // array of dimension sizes
    union libenv_value low;   // minimum value
    union libenv_value high;  // maximum value
};

// Option for environment configuration
struct libenv_option {
    const char *name;
    int dtype;          // libenv_dtype
    int count;          // for arrays/strings
    void *data;         // pointer to data
};

// Options collection
struct libenv_options {
    int count;
    struct libenv_option *items;
};

// Buffer pointers for observations, actions, rewards, and info
struct libenv_buffers {
    int ob_count;
    void **ob;          // observation buffers

    int ac_count;
    void **ac;          // action buffers

    float *rew;         // reward buffer
    uint8_t *first;     // first/done flags

    int info_count;
    const char **info_name;
    void **info;        // info buffers
};

// Opaque environment handle
typedef struct libenv_env_impl libenv_env;

// Core API functions
LIBENV_API int libenv_version(void);
LIBENV_API libenv_env *libenv_make(int num_envs, const struct libenv_options options);
LIBENV_API int libenv_get_tensortypes(libenv_env *handle, enum libenv_space_name name, struct libenv_tensortype *out_types);
LIBENV_API void libenv_set_buffers(libenv_env *handle, struct libenv_buffers *bufs);
LIBENV_API void libenv_observe(libenv_env *handle);
LIBENV_API void libenv_act(libenv_env *handle);
LIBENV_API void libenv_close(libenv_env *handle);

// State management (optional, for save/load functionality)
LIBENV_API int get_state(libenv_env *handle, int env_idx, char *data, int length);
LIBENV_API void set_state(libenv_env *handle, int env_idx, char *data, int length);

#ifdef __cplusplus
}
#endif

#endif // LIBENV_H
