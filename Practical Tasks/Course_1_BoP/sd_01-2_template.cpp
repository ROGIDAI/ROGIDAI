#include <iostream>

using namespace std;

//----- Globalus kintamieji ---------------------------------------------------

const int N = 50;           // Geografiniu tasku skaicius
double coord[N][2];         // Geografiniu tasku koordinates
int pop[N];                 // Geografiniu tasku perkamosios galios (populiacijos)

int numP = 5;               // Rinkoje egzistuojanciu objektu skaicius
int P[] = {0,1,2,3,4};      // Rinkoje egzistuojanciu objektu indeksai masyvuose (coord) ir (pop)

//----- Funkciju prototipai ---------------------------------------------------

void readFile();                                        // Nuskaitomi koordinaciu ir populiacijos duomenys is failo
void printData();                                       // Atspausdinami visi koordinaciu ir populiacijos duomenys
void printData(int n);                                  // Atspausdinamas nurodytas kiekis (n) koordinaciu ir populiacijos duomenu
double HaversineDistance(int i, int j);                 // Atstumas (km) tarp dvieju geografiniu tasku, kuriu indeksai masyve yra (i) ir (j)
double getClosestDistance(int i, int* F, int numF);     // Randamas atstumas nuo geografinio tasko (i) iki artimiausio objekto aibeje (F), kurioje yra (numF) objektu indeksai
double getUtilityOfX(int* X, int numX);                 // Perkamoji galia tenkanti naujiems objektams aibėje (X), kurioje yra (numX) objektų indeksai

//----- Pagrinine funkcija ----------------------------------------------------

int main() {
    int numX = 3;                                       // Nauju objektu skaicius
    int X[] = {5,6,7};                                  // objektu indeksai

    readFile();                                         // Nuskaito duomenis is failo
    printData(3);                                       // Atspausdina tris pirmuosius irasus
    cout << HaversineDistance(0,1) << endl;             // Output: 93.9964
    cout << getClosestDistance(0, P, numP) << endl;     // Output: 0
    cout << getClosestDistance(0, X, numX) << endl;     // Output: 18.4549
    cout << getUtilityOfX(X, numX) << endl;             // Output: 15.7809
}