#ifndef PLUGIN_INTERFACE_H
#define PLUGIN_INTERFACE_H

typedef struct {
    const char *name;
    const char *version;
    int (*initialize)(void);
    int (*execute)(const char *args);
    void (*cleanup)(void);
} plugin_info_t;

#define PLUGIN_EXPORT __attribute__((visibility("default")))

#endif