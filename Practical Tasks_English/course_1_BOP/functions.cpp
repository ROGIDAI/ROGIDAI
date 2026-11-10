
#include <iostream>
#include <fstream>
#include <cmath>
#include <limits>
#include <iomanip>
#include <vector>

#include "functions.h"

using namespace std;


void readFile() {

    ifstream file("data.dat");

    if (!file.is_open()) {
        cerr << "Error: Cannot open data.dat" << endl;
        return;
    }

    // Step 1: Count the geographical points
    double lat, lon;
    int population;

    numPoints = 0;

    while (file >> lat >> lon >> population) {
        numPoints++;
    }

    file.close();

    if (numPoints == 0) {
        cerr << "Error: No geographical data found." << endl;
        return;
    }

    // Step 2: Allocate dynamic memory
    delete[] points;
    points = new GeoPoint[numPoints];

    // Step 3: Reopen the file and read the data
    file.open("data.dat");

    if (!file.is_open()) {
        cerr << "Error: Cannot reopen data.dat" << endl;
        delete[] points;
        points = nullptr;
        numPoints = 0;
        return;
    }

    for (int i = 0; i < numPoints; i++) {

        if (!(file >> points[i].latitude
                   >> points[i].longitude
                   >> points[i].population)) {
            cerr << "Error reading record " << i << endl;
            file.close();
            delete[] points;
            points = nullptr;
            numPoints = 0;
            return;
        }
    }

    file.close();

    cout << "Successfully loaded "
         << numPoints
         << " geographical points." << endl;
}

void printData(int n) {

    if (points == nullptr) {
        cout << "No geographical data loaded." << endl;
        return;
    }

    if (n < 0) n = 0;
    if (n > numPoints) n = numPoints;

    cout << "Index\tLatitude\tLongitude\tPopulation" << endl;

    for (int i = 0; i < n; i++) {
        cout << i << "\t"
             << points[i].latitude << "\t\t"
             << points[i].longitude << "\t\t"
             << points[i].population << endl;
    }
}

void printData() {
    printData(numPoints);
}



// void printData(int n) {
//     if (n < 0) n = 0;
//     if (n > N) n = N;

//     cout << "Index\tLatitude\tLongitude\tPopulation" << endl;

//     for (int i = 0; i < n; i++) {
//         cout << i << "\t"
//              << coord[i][0] << "\t\t"
//              << coord[i][1] << "\t\t"
//              << pop[i] << endl;
//     }
// }

// void printData() {
//     printData(N);
// }


// double HaversineDistance(int i, int j) {

//     double lat1 = coord[i][0];
//     double lon1 = coord[i][1];

//     double lat2 = coord[j][0];
//     double lon2 = coord[j][1];

//     // Difference between the two coordinates
//     double dlat = fabs(lat1 - lat2);
//     double dlon = fabs(lon1 - lon2);

//     // Degrees to radians conversion
//     double rad = 0.01745;

//     // Haversine formula
//     double a = pow(sin(dlat / 2 * rad), 2)
//              + cos(lat1 * rad) * cos(lat2 * rad)
//              * pow(sin(dlon / 2 * rad), 2);

//     double c = 2 * atan2(sqrt(a), sqrt(1 - a));

//     // Earth's radius in kilometres
//     double distance = 6371 * c;

//     return distance;
// }



double HaversineDistance(
    const GeoPoint* point1,
    const GeoPoint* point2
) {
    double lat1 = point1->latitude;
    double lon1 = point1->longitude;

    double lat2 = point2->latitude;
    double lon2 = point2->longitude;

    // Calculate coordinate differences
    double dlat = fabs(lat1 - lat2);
    double dlon = fabs(lon1 - lon2);

    // Degrees to radians conversion
    double rad = 0.01745;

    // Haversine formula
    double a = pow(sin(dlat / 2 * rad), 2)
             + cos(lat1 * rad) * cos(lat2 * rad)
             * pow(sin(dlon / 2 * rad), 2);

    double c = 2 * atan2(sqrt(a), sqrt(1 - a));

    // Earth's radius in kilometres
    double distance = 6371 * c;

    return distance;
}




double getClosestDistance(int i, int* F, int numF) {

    double minDistance = numeric_limits<double>::infinity();

    for (int k = 0; k < numF; k++) {

        int facilityIndex = F[k];

       // double distance = HaversineDistance(i, facilityIndex);
        double distance = HaversineDistance(
            &points[i],
            &points[facilityIndex]
        );

        if (distance < minDistance) {
            minDistance = distance;
        }
    }

    return minDistance;
}


// double getUtilityOfX(int* X, int numX) {

//     double capturedPopulation = 0.0;
//     double totalPopulation = 0.0;

//     for (int i = 0; i < N; i++) {

//         // Add population of the geographical point
//         totalPopulation += pop[i];

//         // Distance to nearest existing facility
//         double distExisting = getClosestDistance(i, P, numP);

//         // Distance to nearest new facility
//         double distNew = getClosestDistance(i, X, numX);

//         // Calculate captured population
//         if (distNew < distExisting) {
//             capturedPopulation += pop[i];
//         }
//         else if (distNew == distExisting) {
//             capturedPopulation += pop[i] / 3.0;
//         }
//     }

//     // Return captured market share as percentage
//     if (totalPopulation == 0.0) {
//         return 0.0;
//     }

//     return (capturedPopulation / totalPopulation) * 100.0;
// }



double getUtilityOfX(int* X, int numX, int demandCount) {

    if (points == nullptr || demandCount <= 0) {
        return 0.0;
    }

    if (demandCount > numPoints) {
        demandCount = numPoints;
    }

    double capturedPopulation = 0.0;
    double totalPopulation = 0.0;

    for (int i = 0; i < demandCount; i++) {

        totalPopulation += points[i].population;

        double distExisting =
            getClosestDistance(i, P, numP);

        double distNew =
            getClosestDistance(i, X, numX);

        if (distNew < distExisting) {
            capturedPopulation += points[i].population;
        }
        else if (distNew == distExisting) {
            capturedPopulation +=
                points[i].population / 3.0;
        }
    }

    if (totalPopulation == 0.0) {
        return 0.0;
    }

    return (capturedPopulation / totalPopulation) * 100.0;
}



double** createDistanceMatrix(const GeoPoint* data, int n) {

    // Allocate memory for row pointers
    double** matrix = new double*[n];

    // Allocate and calculate each row
    for (int i = 0; i < n; i++) {

        // Row i contains i+1 elements
        matrix[i] = new double[i + 1];

        for (int j = 0; j <= i; j++) {

            if (i == j) {
                matrix[i][j] = 0.0;
            }
            else {
                matrix[i][j] = HaversineDistance(
                    &data[i],
                    &data[j]
                );
            }
        }
    }

    return matrix;
}


void printDistanceMatrix(double** matrix, int n) {

    if (matrix == nullptr || n <= 0) {
        cout << "Invalid matrix or number of rows." << endl;
        return;
    }

    // Preserve original output formatting
    ios::fmtflags oldFlags = cout.flags();
    streamsize oldPrecision = cout.precision();

    cout << fixed << setprecision(1);

    for (int i = 0; i < n; i++) {

        for (int j = 0; j <= i; j++) {

            cout << setw(8) << matrix[i][j];
        }

        cout << endl;
    }

    // Restore original output formatting
    cout.flags(oldFlags);
    cout.precision(oldPrecision);
}



double getDistanceFromMatrix(double** matrix, int i, int j) {

    if (i >= j) {
        return matrix[i][j];
    }
    else {
        return matrix[j][i];
    }
}

// complete enumeration function 
void enumerateCombinations(int candidateCount, int n) {

    if (n < 1 || n > candidateCount) {
        cout << "Invalid number of new facilities." << endl;
        return;
    }

    // Initial solution: {0, 1, 2, ...}
    vector<int> X(n);

    for (int i = 0; i < n; i++) {
        X[i] = i;
    }

    long long combinationCount = 0;
    long long evaluationCount = 0;

    // variable store best utility and solution
    double bestUtility = -1.0;
    vector<int> bestX;


    while (true) {

        // Count the current solution
        combinationCount++;

    // Evaluate market share for the current solution
    double utility = getUtilityOfX(
        X.data(),
        n,
        TASK1_COUNT
    );

    evaluationCount++;
    
    if (utility > bestUtility) {
        bestUtility = utility;
        bestX = X;
    }

        

        // Display the first five combinations
        if (combinationCount <= 5) {
            cout << "Combination " << combinationCount << ": {";

            for (int j = 0; j < n; j++) {
                cout << X[j];
                if (j < n - 1) cout << ", ";
            }


            cout << "} - Market share: "
                << utility << "%" << endl;

           

        }


        // Find the rightmost position that can increase
        int i = n - 1;

        while (i >= 0 && X[i] == candidateCount - n + i) {
            i--;
        }

        // No further combinations
        if (i < 0) {
            break;
        }

        // Increase the selected position
        X[i]++;

        // Reset subsequent positions
        for (int j = i + 1; j < n; j++) {
            X[j] = X[j - 1] + 1;
        }
    }

    // Display the last combination
    cout << "Last combination: {";

    for (int j = 0; j < n; j++) {
        cout << X[j];
        if (j < n - 1) cout << ", ";
    }

    cout << "}" << endl;


cout << "Total combinations generated: "
     << combinationCount << endl;

cout << "Total combinations evaluated: "
     << evaluationCount << endl;

// print the best solution 

cout << "\n--- Optimal Facility Locations ---\n";

cout << "Best combination: {";

for (int j = 0; j < n; j++) {
    cout << bestX[j];
    if (j < n - 1) {
        cout << ", ";
    }
}

cout << "}" << endl;

cout << "Maximum market share: "
     << fixed << setprecision(4)
     << bestUtility << "%" << endl;




}

