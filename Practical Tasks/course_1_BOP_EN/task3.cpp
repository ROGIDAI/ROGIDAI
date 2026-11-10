#include <iostream>
#include <fstream>
#include <cmath>
#include <limits>
#include <iomanip>
#include <vector>
#include "functions.h"


using namespace std;


// Pointer for dynamically allocated geographical points
GeoPoint* points = nullptr;

// Number of geographical points loaded
int numPoints = 0;


int numP = 5;               // Rinkoje egzistuojanciu objektu skaicius
int P[] = {0,1,2,3,4};      // Rinkoje egzistuojanciu objektu indeksai masyvuose (coord) ir (pop)




int main() {

    readFile();

    if (points == nullptr) {
        return 1;
    }



cout << "\n--- Complete Enumeration Test ---\n";

int candidateCount = 50;
int numNewFacilities = 3;

enumerateCombinations(candidateCount, numNewFacilities);



// Test the distance matrix creation code...

cout << "\n--- Triangular Distance Matrix Test ---\n";

int matrixSize = 500; // distance matrix size

double** distanceMatrix =
    createDistanceMatrix(points, matrixSize);




cout << "\n--- Large Matrix Verification ---\n";

double matrixDistance =
    getDistanceFromMatrix(distanceMatrix, 0, 499);

double directDistance =
    HaversineDistance(&points[0], &points[499]);

cout << "Matrix distance (0,499): "
     << matrixDistance << " km" << endl;

cout << "Direct Haversine distance (0,499): "
     << directDistance << " km" << endl;

if (fabs(matrixDistance - directDistance) < 1e-9) {
    cout << "Verification: PASSED" << endl;
}
else {
    cout << "Verification: FAILED" << endl;
}


// check distance retrieval for dist..matrix
cout << "\n--- Distance Retrieval Test ---\n";

cout << "Distance (0,1): "
     << getDistanceFromMatrix(distanceMatrix, 0, 1)
     << " km" << endl;

cout << "Distance (1,0): "
     << getDistanceFromMatrix(distanceMatrix, 1, 0)
     << " km" << endl;

cout << "Distance (2,0): "
     << getDistanceFromMatrix(distanceMatrix, 2, 0)
     << " km" << endl;

cout << "Distance (0,2): "
     << getDistanceFromMatrix(distanceMatrix, 0, 2)
     << " km" << endl;

cout << "Distance (2,2): "
     << getDistanceFromMatrix(distanceMatrix, 2, 2)
     << " km" << endl;


cout << "\n--- First 10 Rows of Distance Matrix ---\n";

printDistanceMatrix(distanceMatrix, 10); // Print first n rows of the distance matrix

cout << "Matrix created for "
     << matrixSize << " points." << endl;

cout << "Distance (0,0): "
     << distanceMatrix[0][0] << " km" << endl;

cout << "Distance (1,0): "
     << distanceMatrix[1][0] << " km" << endl;

cout << "Distance (2,0): "
     << distanceMatrix[2][0] << " km" << endl;

cout << "Distance (2,1): "
     << distanceMatrix[2][1] << " km" << endl;

// Release matrix memory after testing
for (int i = 0; i < matrixSize; i++) {
    delete[] distanceMatrix[i];
}

delete[] distanceMatrix;




    // Test HaversineDistance function
    cout << "\n--- Pointer-based Haversine Test ---\n";

    cout << "Distance (0,1): "
        << HaversineDistance(&points[0], &points[1])
        << " km" << endl;

    cout << "Distance (1,0): "
        << HaversineDistance(&points[1], &points[0])
        << " km" << endl;

    cout << "Distance (0,0): "
        << HaversineDistance(&points[0], &points[0])
        << " km" << endl;


    cout << "\n--- Dynamic Memory Test ---\n";

    cout << "Total geographical points: "
         << numPoints << endl;

    cout << "\nFirst geographical point:\n";

    cout << "Latitude: "
         << points[0].latitude << endl;

    cout << "Longitude: "
         << points[0].longitude << endl;

    cout << "Population: "
         << points[0].population << endl;

    cout << "\n--- Original Task 1 Verification ---\n";

    int X[] = {5, 6, 7};

    cout << "Market share: "
         << getUtilityOfX(X, 3) << "%" << endl;

    delete[] points;
    points = nullptr;

    return 0;
}



