#include "bate.h"

#define N (1024*1024)

struct Matrix {
    float m_data[N][N];

    float &at(int x, int y) {
        return m_data[x][y];
    }
};

struct Vector {
    float m_data[N];

    float &at(int x) {
        return m_data[x];
    }
};

int main() {
    bate::timing("main");

    Matrix *a = new Matrix{};
    Vector *v = new Vector{};
    Vector *w = new Vector{};

    for (int i = 0; i < N; i++) {
        v->at(i) = bate::frand();
    }

    for (int i = 0; i < N; i++) {
        a->at(i, i) = 2;
        if (i > 0)
            a->at(i - 1, i) = -1;
        if (i < N - 1)
            a->at(i + 1, i) = -1;
    }

    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            w->at(i) += a->at(i, j) * v->at(j);
        }
    }

    for (int i = 1; i < N - 1; i++) {
        if (std::abs(2 * v->at(i) - v->at(i - 1) - v->at(i + 1) - w->at(i)) > 0.0001f) {
            printf("wrong at %d\n", i);
            return 1;
        }
    }
    printf("all correct\n");

    bate::timing("main");
    return 0;
}
