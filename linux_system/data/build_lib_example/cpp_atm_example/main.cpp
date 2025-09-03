// main.cpp
#include <iostream>
#include "ATM.h"

int main() {
    // Create an instance of the ATM class
    ATM myATM;

    // Deposit some money
    myATM.deposit(1000.0);

    // Check the account balance
    std::cout << "Account Balance: $" << myATM.checkBalance() << std::endl;

    // Withdraw some money
    myATM.withdraw(500.0);

    // Check the updated account balance
    std::cout << "Account Balance after withdrawal: $" << myATM.checkBalance() << std::endl;

    return 0;
}

