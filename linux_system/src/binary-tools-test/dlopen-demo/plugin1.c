#include "plugin_interface.h"
#include <stdio.h>

static int plugin1_init() {
    printf("Plugin 1 initialized\n");
    return 0;
}

static int plugin1_execute(const char *args) {
    printf("Plugin 1 executing with args: %s\n", args ? args : "(none)");
    return 0;
}

static void plugin1_cleanup() {
    printf("Plugin 1 cleanup\n");
}

PLUGIN_EXPORT plugin_info_t plugin_info = {
    .name = "Sample Plugin 1",
    .version = "1.0.0",
    .initialize = plugin1_init,
    .execute = plugin1_execute,
    .cleanup = plugin1_cleanup
};