#include <iostream>
#include <fstream>
#include <cmath>
#include <limits>




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


int main() {
    int numX = 3;
    int X[] = {5, 6, 7};

    readFile();
    printData(3);

    cout << HaversineDistance(0, 1) << endl;
    cout << getClosestDistance(0, P, numP) << endl;
    cout << getClosestDistance(0, X, numX) << endl;
    cout << getUtilityOfX(X, numX) << endl;

    return 0;
}




// int main() {

//     readFile();

//     cout << "\n--- Haversine Distance Test ---\n";

//     cout << "Distance (0,1): "
//          << HaversineDistance(0,1) << " km" << endl;

//     cout << "Distance (1,0): "
//          << HaversineDistance(1,0) << " km" << endl;

//     cout << "Distance (0,0): "
//          << HaversineDistance(0,0) << " km" << endl;

//     return 0;
// }



// int main() {

//     readFile();

//     int numX = 3;
//     int X[] = {5, 6, 7};

//     cout << "\n--- Closest Distance Test ---\n";

//     cout << "Closest existing facility to point 0: "
//          << getClosestDistance(0, P, numP)
//          << " km" << endl;

//     cout << "Closest new facility to point 0: "
//          << getClosestDistance(0, X, numX)
//          << " km" << endl;

//     cout << "Closest new facility to point 5: "
//          << getClosestDistance(5, X, numX)
//          << " km" << endl;

//     return 0;
// }


// int main() {

//     readFile();

//     cout << "\n--- Market Share Tests ---\n";

//     int X1[] = {5, 6, 7};
//     int X2[] = {8, 9, 10};
//     int X3[] = {0, 1, 2};

//     cout << "Test 1 - X = {5,6,7}: "
//          << getUtilityOfX(X1, 3) << "%" << endl;

//     cout << "Test 2 - X = {8,9,10}: "
//          << getUtilityOfX(X2, 3) << "%" << endl;

//     cout << "Test 3 - X = {0,1,2}: "
//          << getUtilityOfX(X3, 3) << "%" << endl;

//     return 0;
// }



void readFile() {
    ifstream file("data.dat");

    if (!file.is_open()) {
        cerr << "Error: Cannot open data.dat" << endl;
        return;
    }

    for (int i = 0; i < N; i++) {
        if (!(file >> coord[i][0] >> coord[i][1] >> pop[i])) {
            cerr << "Error reading record " << i << endl;
            return;
        }
    }

    file.close();

    cout << "Successfully loaded " << N << " geographical points." << endl;
}


void printData(int n) {
    if (n < 0) n = 0;
    if (n > N) n = N;

    cout << "Index\tLatitude\tLongitude\tPopulation" << endl;

    for (int i = 0; i < n; i++) {
        cout << i << "\t"
             << coord[i][0] << "\t\t"
             << coord[i][1] << "\t\t"
             << pop[i] << endl;
    }
}

void printData() {
    printData(N);
}


double HaversineDistance(int i, int j) {

    double lat1 = coord[i][0];
    double lon1 = coord[i][1];

    double lat2 = coord[j][0];
    double lon2 = coord[j][1];

    // Difference between the two coordinates
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

        double distance = HaversineDistance(i, facilityIndex);

        if (distance < minDistance) {
            minDistance = distance;
        }
    }

    return minDistance;
}


double getUtilityOfX(int* X, int numX) {

    double capturedPopulation = 0.0;
    double totalPopulation = 0.0;

    for (int i = 0; i < N; i++) {

        // Add population of the geographical point
        totalPopulation += pop[i];

        // Distance to nearest existing facility
        double distExisting = getClosestDistance(i, P, numP);

        // Distance to nearest new facility
        double distNew = getClosestDistance(i, X, numX);

        // Calculate captured population
        if (distNew < distExisting) {
            capturedPopulation += pop[i];
        }
        else if (distNew == distExisting) {
            capturedPopulation += pop[i] / 3.0;
        }
    }

    // Return captured market share as percentage
    if (totalPopulation == 0.0) {
        return 0.0;
    }

    return (capturedPopulation / totalPopulation) * 100.0;
}
