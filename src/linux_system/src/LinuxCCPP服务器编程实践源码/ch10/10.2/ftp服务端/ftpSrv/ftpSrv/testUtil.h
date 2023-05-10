#pragma once

#include <iostream>
using namespace std;

#ifdef TEST
#define testout(msg) cout << msg << endl << flush
#else
#define testout(msg)
#endif
