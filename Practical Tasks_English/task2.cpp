#include <iostream>
#include <fstream>
#include <cmath>
#include <limits>
#include <iomanip>


using namespace std;

struct GeoPoint {
    double latitude;
    double longitude;
    int population;
};

// Pointer for dynamically allocated geographical points
GeoPoint* points = nullptr;

// Number of geographical points loaded
int numPoints = 0;


//----- Globalus kintamieji ---------------------------------------------------

// const int N = 50;           // Geografiniu tasku skaicius
// double coord[N][2];         // Geografiniu tasku koordinates
// int pop[N];                 // Geografiniu tasku perkamosios galios (populiacijos)

const int TASK1_COUNT = 50;


int numP = 5;               // Rinkoje egzistuojanciu objektu skaicius
int P[] = {0,1,2,3,4};      // Rinkoje egzistuojanciu objektu indeksai masyvuose (coord) ir (pop)

//----- Funkciju prototipai ---------------------------------------------------

void readFile();                                        // file read function  Nuskaitomi koordinaciu ir populiacijos duomenys is failo
void printData();                                       // Atspausdinami visi koordinaciu ir populiacijos duomenys
void printData(int n);                                  // Atspausdinamas nurodytas kiekis (n) koordinaciu ir populiacijos duomenu
// double HaversineDistance(int i, int j);                 // Atstumas (km) tarp dvieju geografiniu tasku, kuriu indeksai masyve yra (i) ir (j)
double getClosestDistance(int i, int* F, int numF);     // Randamas atstumas nuo geografinio tasko (i) iki artimiausio objekto aibeje (F), kurioje yra (numF) objektu indeksai
//double getUtilityOfX(int* X, int numX);                 // Perkamoji galia tenkanti naujiems objektams aibėje (X), kurioje yra (numX) objektų indeksai
double getUtilityOfX(
    int* X,
    int numX,
    int demandCount = TASK1_COUNT
);



double** createDistanceMatrix(const GeoPoint* data, int n); // Create a distance matrix for n number of geographical points

void printDistanceMatrix(double** matrix, int n); //function for print distance matrix

double getDistanceFromMatrix(double** matrix, int i, int j); //get distance from distance matrix containing two geographical points



//----- Pagrinine funkcija ----------------------------------------------------

// int main() {
//     int numX = 3;                                       // Nauju objektu skaicius
//     int X[] = {5,6,7};                                  // objektu indeksai

//     readFile();                                         // Nuskaito duomenis is failo
//     printData(3);                                       // Atspausdina tris pirmuosius irasus
//     cout << HaversineDistance(0,1) << endl;             // Output: 93.9964
//     cout << getClosestDistance(0, P, numP) << endl;     // Output: 0
//     cout << getClosestDistance(0, X, numX) << endl;     // Output: 18.4549
//     cout << getUtilityOfX(X, numX) << endl;             // Output: 15.7809
// }


// int main() {
//     int numX = 3;
//     int X[] = {5, 6, 7};

//     readFile();
//     printData(3);

//     cout << HaversineDistance(0, 1) << endl;
//     cout << getClosestDistance(0, P, numP) << endl;
//     cout << getClosestDistance(0, X, numX) << endl;
//     cout << getUtilityOfX(X, numX) << endl;

//     return 0;
// }


// harvesine distance function that takes two GeoPoint pointers as input

double HaversineDistance(
    const GeoPoint* point1,
    const GeoPoint* point2
);


int main() {

    readFile();

    if (points == nullptr) {
        return 1;
    }

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
