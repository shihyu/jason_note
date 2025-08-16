#include "my_application.h"
#include <cstdio>

int main(int argc, char** argv) {
    printf("[INTIFACE_LOG] Linux GTK main() - 啟動 Intiface Central\n");
    printf("sssssssssssssssssssssssssssssssss\n");
  g_autoptr(MyApplication) app = my_application_new();
  printf("[INTIFACE_LOG] Linux GTK main() - 建立 GTK 應用程式完成，準備運行\n");
  return g_application_run(G_APPLICATION(app), argc, argv);
}
