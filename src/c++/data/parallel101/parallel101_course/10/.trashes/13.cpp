#include "bate.h"

#define N (1024*1024)
#define B 8

struct Matrix {
    struct Block {
        float m_block[B][B]{};
    };

    std::map<std::tuple<int, int>, Block> m_data;

    float &at(int x, int y) {
        return m_data[std::make_tuple(x / B, y / B)].m_block[x % B][y % B];
    }

    template <class Func>
    void foreach(Func &&func) {
        for (auto &[key, value]: m_data) {
            auto &[x, y] = key;
            for (int dx = 0; dx < B; dx++) {
                for (int dy = 0; dy < B; dy++) {
                    func(x * B + dx, y * B + dy);
                }
            }
        }
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

    a->foreach([&] (int i, int j) {
        w->at(i) += a->at(i, j) * v->at(j);
    });

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
