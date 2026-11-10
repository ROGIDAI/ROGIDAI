#include <iostream>
#include <time.h>
#include <sys/time.h>
#include <cmath>

using namespace std;

//===== Global variables =======================================================

int num_points = 5000;      		// Number of points (max 50000). More points increase matrix calculation and solution search time
int num_variables = 3;      		// Number of points to find
int num_possible_locations = 50;	// Number of possible locations for new facilities (first points in the array)

double **points;            		// Array for storing points
double **distance_matrix;   		// Array for storing the distance matrix

//===== Function declarations ==================================================

double get_time();                                          // Function for measuring time
void load_data();                                           // Function for loading data from a file
double Haversine_distance(double, double, double, double);  // Function for calculating distance using the Haversine formula
double distance_from_matrix(int, int);                      // Function for getting a distance from the distance matrix
bool next_solution(int*); 									// Function for generating the next solution
double evaluate_solution(int*);                             // Function for evaluating the objective function value of a solution

//=============================================================================

int main() {
	
    srand(time(NULL));

	double t_0 = get_time();    // Record the program start time
		
    load_data();                // Load data from the file
	
	double t_1 = get_time();    // Record the end of data loading
	
    //-------------------------------------------------------------------------
	// Calculate the distance matrix
    // The matrix is triangular because the distance from A to B equals the distance from B to A
    //-------------------------------------------------------------------------

	distance_matrix = new double*[num_points];
	for (int i=0; i<num_points; i++) {
		distance_matrix[i] = new double[i+1];
		for (int j=0; j<=i; j++) {
			distance_matrix[i][j] = Haversine_distance(points[i][0], points[i][1], points[j][0], points[j][1]);
		}
	}
	
	double t_2 = get_time();    // Record the end of distance matrix calculation
	
    //-------------------------------------------------------------------------
	// Search for the best solution using complete enumeration
    // (English: Complete Enumeration)
    //-------------------------------------------------------------------------
	
    int *solution = new int[num_variables];       // Array for storing a randomly generated solution
    int *best_solution = new int[num_variables];  // Array for storing the best solution found
	double f_solution, f_best_solution = 1e10;     // Objective function values for the random and best solutions found

	for (int i=0; i<num_variables; i++) solution[i] = i;	// Initial solution [0, 1, 2]
	//for (int i=0; i<num_variables; i++) cout << solution[i] << " "; cout << endl;

	while (next_solution(solution) == true) {
		f_solution = evaluate_solution(solution);   // Calculate the objective function value of the solution
		if (f_solution < f_best_solution) {         // Check whether the generated solution is better (smaller) than the best known solution
			f_best_solution = f_solution;            // If so, update the best known solution
			for (int j=0; j<num_variables; j++) {
                best_solution[j] = solution[j];
            }
		}
	}

	double t_3 = get_time();    // Record the end of solution search

    //-------------------------------------------------------------------------
	// Print the results
    //-------------------------------------------------------------------------


	cout << "Best solution found (point indices in the data array): ";
	for (int i=0; i<num_variables; i++) cout << best_solution[i] << "\t";
	cout << endl;
	cout << "Data loading time: " << t_1 - t_0 << " s." << endl;
	cout << "Distance matrix calculation time: " << t_2 - t_1 << " s." << endl;
	cout << "Solution search time: " << t_3 - t_2 << " s." << endl;
	
}

//=============================================================================
// Helper functions. THESE FUNCTIONS DO NOT NEED TO BE PARALLELIZED.
//=============================================================================

double get_time() {
   struct timeval laikas;
   gettimeofday(&laikas, NULL);
   double rez = (double)laikas.tv_sec+(double)laikas.tv_usec/1000000;
   return rez;
}

//=============================================================================

void load_data() {
	
	//----- Load demand points ------------------------------------------------
	FILE *f;
	f = fopen("lab_data.dat", "r");
	points = new double*[num_points];
	for (int i=0; i<num_points; i++) {
		points[i] = new double[2];
		fscanf(f, "%lf%lf", &points[i][0], &points[i][1]);
	}
	fclose(f);
}

//=============================================================================

double Haversine_distance(double lat1, double lon1, double lat2, double lon2) {
	double dlat = fabs(lat1 - lat2);
	double dlon = fabs(lon1 - lon2);
	double aa = pow((sin((double)dlat/(double)2*0.01745)),2) + cos(lat1*0.01745) *
               cos(lat2*0.01745) * pow((sin((double)dlon/(double)2*0.01745)),2);
	double c = 2 * atan2(sqrt(aa), sqrt(1-aa));
	double d = 6371 * c; 
	return d;
}

//=============================================================================

double distance_from_matrix(int i, int j) {
	if (i >= j)	return distance_matrix[i][j];
	else return distance_matrix[j][i];
}

//=============================================================================

bool next_solution(int *solution) {
    int k = num_variables;
	int n = num_possible_locations;

	int i = k - 1;
    while (i >= 0 && solution[i] == n - k + i) i--;
    if (i < 0) return false;
    solution[i]++;
    for (int j = i + 1; j < k; j++) {
        solution[j] = solution[j - 1] + 1;
    }
    return true;
}

//=============================================================================

double evaluate_solution(int *solution) {
	double distance, min_distance, total_distance = 0;	
	for (int i=0; i<num_points; i++) {
        min_distance = 1e10;
        for (int j=0; j<num_variables; j++) {
		    distance = distance_from_matrix(i, solution[j]);
            if (distance < min_distance) {
                min_distance = distance;
            }
        }
        total_distance += min_distance;		    
    }
	return total_distance;
}

//=============================================================================