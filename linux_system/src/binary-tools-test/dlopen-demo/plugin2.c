#include "plugin_interface.h"
#include <stdio.h>

static int plugin2_init() {
    printf("Plugin 2 initialized\n");
    return 0;
}

static int plugin2_execute(const char *args) {
    printf("Plugin 2 executing with args: %s\n", args ? args : "(none)");
    return 0;
}

static void plugin2_cleanup() {
    printf("Plugin 2 cleanup\n");
}

PLUGIN_EXPORT plugin_info_t plugin_info = {
    .name = "Sample Plugin 2",
    .version = "2.0.0",
    .initialize = plugin2_init,
    .execute = plugin2_execute,
    .cleanup = plugin2_cleanup
};