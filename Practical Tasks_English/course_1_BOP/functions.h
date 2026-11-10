
#ifndef BOP_FUNCTIONS_H
#define BOP_FUNCTIONS_H

// Structure for geographical data
struct GeoPoint {
    double latitude;
    double longitude;
    int population;
};

// Number of points used for Task 1 verification
constexpr int TASK1_COUNT = 50;

// Global variables defined in task3.cpp
extern GeoPoint* points;
extern int numPoints;
extern int numP;
extern int P[];

// Data handling functions
void readFile();
void printData();
void printData(int n);

// Distance calculations
double HaversineDistance(
    const GeoPoint* point1,
    const GeoPoint* point2
);

double getClosestDistance(int i, int* F, int numF);

// Market share evaluation
double getUtilityOfX(
    int* X,
    int numX,
    int demandCount = TASK1_COUNT
);

// Distance matrix functions
double** createDistanceMatrix(const GeoPoint* data, int n);

void printDistanceMatrix(double** matrix, int n);

double getDistanceFromMatrix(
    double** matrix,
    int i,
    int j
);

// Complete enumeration
void enumerateCombinations(int candidateCount, int n);

#endif
