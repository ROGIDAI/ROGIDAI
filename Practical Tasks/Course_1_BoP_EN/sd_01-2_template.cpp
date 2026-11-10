#include <iostream>

using namespace std;

//----- Global variables -------------------------------------------------------

const int N = 50;           // Number of geographic points
double coord[N][2];         // Coordinates of geographic points
int pop[N];                 // Buying power (population) of geographic points

int numP = 5;               // Number of existing facilities in the market
int P[] = {0,1,2,3,4};      // Indices of existing facilities in coord and pop arrays

//----- Function declarations --------------------------------------------------

void readFile();                                        // Read coordinates and population data from a file
void printData();                                       // Print all coordinates and population data
void printData(int n);                                  // Print the first n coordinate and population records
double HaversineDistance(int i, int j);                 // Distance (km) between geographic points i and j
double getClosestDistance(int i, int* F, int numF);     // Distance from point i to the nearest facility in F (numF facilities)
double getUtilityOfX(int* X, int numX);                 // Buying power gained by new facilities in X (numX facilities)

//----- Main function ---------------------------------------------------------

int main() {
    int numX = 3;                                       // Number of new facilities
    int X[] = {5,6,7};                                  // Facility indices

    readFile();                                         // Read data from a file
    printData(3);                                       // Print the first three records
    cout << HaversineDistance(0,1) << endl;             // Output: 93.9964
    cout << getClosestDistance(0, P, numP) << endl;     // Output: 0
    cout << getClosestDistance(0, X, numX) << endl;     // Output: 18.4549
    cout << getUtilityOfX(X, numX) << endl;             // Output: 15.7809
}