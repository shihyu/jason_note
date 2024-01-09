// ATM.cpp
#include "ATM.h"
#include <iostream>


ATM::ATM() {
    // Initialize balance to zero
    balance = 0.0;
}

ATM::~ATM() {
    // Destructor implementation (if needed)
}

double ATM::checkBalance() {
    return balance;
}

void ATM::deposit(double amount) {
    balance += amount;
}

void ATM::withdraw(double amount) {
    if (amount <= balance) {
        balance -= amount;
    } else {
        // Handle insufficient funds
        // For simplicity, we can just print an error message
        std::cout << "Insufficient funds!" << std::endl;
    }
}

