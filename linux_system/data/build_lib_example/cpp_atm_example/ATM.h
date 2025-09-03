// ATM.h
#ifndef ATM_H
#define ATM_H

class ATM {
public:
    ATM();  // Constructor
    ~ATM(); // Destructor

    // Function to check account balance
    double checkBalance();

    // Function to deposit money
    void deposit(double amount);

    // Function to withdraw money
    void withdraw(double amount);

private:
    double balance;
};

#endif // ATM_H

