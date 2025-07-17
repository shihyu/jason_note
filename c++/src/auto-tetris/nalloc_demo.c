#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "nalloc.h"

/* 演示用的數據結構 */
typedef struct {
    int width, height;
    int** data;      /* 2D數組 */
    char* name;      /* 矩陣名稱 */
    float* weights;  /* 權重數組 */
} matrix_t;

typedef struct {
    char* name;
    int age;
    char** hobbies;  /* 愛好列表 */
    int hobby_count;
} person_t;

typedef struct {
    char* university;
    person_t** students;  /* 學生列表 */
    int student_count;
    matrix_t* grade_matrix;  /* 成績矩陣 */
} school_t;

/* 輔助函數：打印內存統計信息 */
void print_stats(const char* label, void* ptr)
{
    nalloc_stats_t stats;

    if (nalloc_get_stats(ptr, & stats) == 0) {
        printf("📊 %s 統計:\n", label);
        printf("   子節點數量: %d\n", stats.child_count);
        printf("   樹的深度: %d\n", stats.depth);
        printf("   直接大小: %zu bytes\n", stats.direct_size);
        printf("   總大小: %zu bytes\n\n", stats.total_size);
    }
}

/* 演示1: 基本用法 - 簡單的父子關係 */
void demo_basic_usage(void)
{
    printf("🔥 演示1: 基本用法\n");
    printf("==================\n");

    /* 創建根節點 */
    char* root = nalloc(100, NULL);
    strcpy(root, "這是根節點");
    printf("✓ 創建根節點: %s\n", root);

    /* 創建子節點 */
    char* child1 = nalloc(50, root);
    strcpy(child1, "子節點1");
    printf("✓ 創建子節點1: %s\n", child1);

    char* child2 = nalloc(50, root);
    strcpy(child2, "子節點2");
    printf("✓ 創建子節點2: %s\n", child2);

    /* 創建孫子節點 */
    char* grandchild = nalloc(30, child1);
    strcpy(grandchild, "孫子節點");
    printf("✓ 創建孫子節點: %s\n", grandchild);

    print_stats("根節點", root);

    /* 一鍵清理所有相關內存 */
    printf("🗑️ 釋放根節點，自動清理整個樹...\n");
    nfree(root);
    printf("✅ 所有內存已自動清理完成!\n\n");
}

/* 演示2: 矩陣分配 - 複雜的2D數組管理 */
matrix_t* create_matrix(int width, int height, const char* name)
{
    /* 創建矩陣結構 */
    matrix_t* m = nalloc(sizeof(matrix_t), NULL);

    if (!m) return NULL;

    m->width = width;
    m->height = height;

    /* 矩陣名稱 */
    m->name = nalloc(strlen(name) + 1, m);
    strcpy(m->name, name);

    /* 分配行指針數組 */
    m->data = ncalloc(height, sizeof(int*), m);

    /* 分配每一行 */
    for (int i = 0; i < height; i++) {
        m->data[i] = ncalloc(width, sizeof(int), m->data);

        /* 填充一些示例數據 */
        for (int j = 0; j < width; j++) {
            m->data[i][j] = i* width + j;
        }
    }

    /* 權重數組 */
    m->weights = ncalloc(width* height, sizeof(float), m);

    for (int i = 0; i < width* height; i++) {
        m->weights[i] = (float)i / (width* height);
    }

    return m;
}

void print_matrix(matrix_t* m)
{
    printf("矩陣 '%s' (%dx%d):\n", m->name, m->width, m->height);

    for (int i = 0; i < m->height; i++) {
        printf("  ");

        for (int j = 0; j < m->width; j++) {
            printf("%3d ", m->data[i][j]);
        }

        printf("\n");
    }

    printf("  權重前5個: %.2f, %.2f, %.2f, %.2f, %.2f\n",
           m->weights[0], m->weights[1], m->weights[2], m->weights[3], m->weights[4]);
}

void demo_matrix_allocation(void)
{
    printf("🔥 演示2: 矩陣分配\n");
    printf("==================\n");

    matrix_t* matrix = create_matrix(4, 3, "演示矩陣");
    print_matrix(matrix);
    print_stats("矩陣", matrix);

    printf("🗑️ 釋放矩陣...\n");
    nfree(matrix);
    printf("✅ 矩陣及所有相關內存已自動清理!\n\n");
}

/* 演示3: 動態重新分配父子關係 */
void demo_reparenting(void)
{
    printf("🔥 演示3: 動態重新分配父子關係\n");
    printf("===============================\n");

    /* 創建兩個獨立的根節點 */
    char* root1 = nalloc(50, NULL);
    strcpy(root1, "根節點1");

    char* root2 = nalloc(50, NULL);
    strcpy(root2, "根節點2");

    /* 在root1下創建子節點 */
    char* child = nalloc(50, root1);
    strcpy(child, "可移動的子節點");

    printf("✓ 初始狀態: '%s' 是 '%s' 的子節點\n", child, root1);
    print_stats("根節點1", root1);
    print_stats("根節點2", root2);

    /* 將子節點移動到root2下 */
    printf("🔄 將子節點從根節點1移動到根節點2...\n");
    nalloc_set_parent(child, root2);

    printf("✓ 移動後: '%s' 現在是 '%s' 的子節點\n", child, root2);
    print_stats("根節點1", root1);
    print_stats("根節點2", root2);

    /* 清理 */
    printf("🗑️ 釋放根節點2（包含移動過來的子節點）...\n");
    nfree(root2);

    printf("🗑️ 釋放根節點1...\n");
    nfree(root1);

    printf("✅ 所有內存已清理!\n\n");
}

/* 演示4: 複雜的嵌套結構 */
person_t* create_person(const char* name, int age, const char** hobbies,
                        int hobby_count, void* parent)
{
    person_t* p = nalloc(sizeof(person_t), parent);

    if (!p) return NULL;

    /* 姓名 */
    p->name = nalloc(strlen(name) + 1, p);
    strcpy(p->name, name);

    p->age = age;
    p->hobby_count = hobby_count;

    /* 愛好列表 */
    p->hobbies = ncalloc(hobby_count, sizeof(char*), p);

    for (int i = 0; i < hobby_count; i++) {
        p->hobbies[i] = nalloc(strlen(hobbies[i]) + 1, p->hobbies);
        strcpy(p->hobbies[i], hobbies[i]);
    }

    return p;
}

school_t* create_school(const char* university_name)
{
    school_t* school = nalloc(sizeof(school_t), NULL);

    if (!school) return NULL;

    /* 大學名稱 */
    school->university = nalloc(strlen(university_name) + 1, school);
    strcpy(school->university, university_name);

    /* 創建一些學生 */
    school->student_count = 3;
    school->students = ncalloc(school->student_count, sizeof(person_t*), school);

    const char* alice_hobbies[] = {"程式設計", "閱讀", "游泳"};
    const char* bob_hobbies[] = {"音樂", "電影"};
    const char* charlie_hobbies[] = {"運動", "旅行", "攝影", "烹飪"};

    school->students[0] = create_person("Alice", 20, alice_hobbies, 3,
                                        school->students);
    school->students[1] = create_person("Bob", 22, bob_hobbies, 2,
                                        school->students);
    school->students[2] = create_person("Charlie", 21, charlie_hobbies, 4,
                                        school->students);

    /* 創建成績矩陣 */
    school->grade_matrix = create_matrix(5, 3, "學生成績");
    nalloc_set_parent(school->grade_matrix, school);

    return school;
}

void print_school(school_t* school)
{
    printf("🏫 大學: %s\n", school->university);
    printf("👥 學生列表:\n");

    for (int i = 0; i < school->student_count; i++) {
        person_t* student = school->students[i];
        printf("  %d. %s (年齡: %d)\n", i + 1, student->name, student->age);
        printf("     愛好: ");

        for (int j = 0; j < student->hobby_count; j++) {
            printf("%s", student->hobbies[j]);

            if (j < student->hobby_count - 1) printf(", ");
        }

        printf("\n");
    }

    printf("\n📈 ");
    print_matrix(school->grade_matrix);
}

void demo_complex_structures(void)
{
    printf("🔥 演示4: 複雜的嵌套結構\n");
    printf("========================\n");

    school_t* school = create_school("台灣大學");
    print_school(school);
    print_stats("學校", school);

    printf("🗑️ 釋放整個學校結構...\n");
    nfree(school);
    printf("✅ 學校、學生、愛好、成績矩陣等所有內存已自動清理!\n\n");
}

/* 演示5: 內存洩漏對比 */
void demo_memory_leak_comparison(void)
{
    printf("🔥 演示5: 內存洩漏對比\n");
    printf("======================\n");

    printf("❌ 傳統malloc方式 (容易洩漏):\n");
    printf("   char *root = malloc(100);\n");
    printf("   char *child1 = malloc(50);\n");
    printf("   char *child2 = malloc(50);\n");
    printf("   char *grandchild = malloc(30);\n");
    printf("   // 需要手動記住並釋放每個指針\n");
    printf("   free(grandchild);\n");
    printf("   free(child2);\n");
    printf("   free(child1);\n");
    printf("   free(root);\n");
    printf("   // 如果忘記任何一個，就會內存洩漏!\n\n");

    printf("✅ nalloc方式 (自動管理):\n");
    char* root = nalloc(100, NULL);
    char* child1 = nalloc(50, root);
    char* child2 = nalloc(50, root);
    char* grandchild = nalloc(30, child1);

    printf("   char *root = nalloc(100, NULL);\n");
    printf("   char *child1 = nalloc(50, root);\n");
    printf("   char *child2 = nalloc(50, root);\n");
    printf("   char *grandchild = nalloc(30, child1);\n");
    printf("   nfree(root);  // 一行代碼清理所有!\n");

    nfree(root);
    printf("   ✨ 不可能發生內存洩漏!\n\n");
}

/* 演示6: nrealloc功能 */
void demo_realloc(void)
{
    printf("🔥 演示6: 動態調整大小\n");
    printf("======================\n");

    /* 創建可調整大小的緩衝區 */
    char* buffer = nalloc(50, NULL);
    strcpy(buffer, "初始字符串");
    printf("✓ 初始緩衝區 (50 bytes): '%s'\n", buffer);

    /* 創建子節點 */
    char* metadata = nalloc(20, buffer);
    strcpy(metadata, "元數據");
    printf("✓ 子節點: '%s'\n", metadata);

    print_stats("緩衝區", buffer);

    /* 調整大小 */
    printf("🔄 將緩衝區擴大到200字節...\n");
    buffer = nrealloc(buffer, 200);
    strcat(buffer, " - 已擴展!");
    printf("✓ 擴展後: '%s'\n", buffer);

    /* 驗證子節點關係仍然有效 */
    printf("✓ 子節點仍然有效: '%s'\n", metadata);
    print_stats("擴展後的緩衝區", buffer);

    nfree(buffer);
    printf("✅ 緩衝區及子節點已清理!\n\n");
}

int main(void)
{
    printf("🎯 nalloc 演示程序\n");
    printf("=================\n");
    printf("這個程序展示了nalloc的各種功能和優勢\n\n");

    /* 運行所有演示 */
    demo_basic_usage();
    demo_matrix_allocation();
    demo_reparenting();
    demo_complex_structures();
    demo_memory_leak_comparison();
    demo_realloc();

    printf("🎉 所有演示完成!\n");
    printf("🔍 重要特性總結:\n");
    printf("   ✅ 自動依賴管理 - 父節點釋放時自動清理子節點\n");
    printf("   ✅ 動態重新分配 - 可以改變父子關係\n");
    printf("   ✅ 統計信息 - 可以查詢內存使用統計\n");
    printf("   ✅ 防止內存洩漏 - 結構化的內存管理\n");
    printf("   ✅ 兼容realloc - 支持動態調整大小\n");
    printf("   ✅ 零學習成本 - 接口類似malloc/free\n\n");

    printf("💡 適用場景:\n");
    printf("   🎮 遊戲開發 - 複雜的對象關係管理\n");
    printf("   🌐 網路服務器 - 請求相關的資源管理\n");
    printf("   🧮 數據結構 - 樹、圖等複雜結構\n");
    printf("   📊 矩陣運算 - 多維數組的自動清理\n");

    return 0;
}
