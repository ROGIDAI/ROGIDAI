#include <iostream>
#include <math.h>

using namespace std;

double HaversineDistance(double* coordsA, double* coordsB) { // CoordsA = {lat, lon}, CoordsA = {lat, lon}
   double dlat = fabs(coordsA[0] - coordsB[0]);
   double dlon = fabs(coordsA[1] - coordsB[1]);   
   double aa = pow((sin((double)dlat/(double)2*0.01745)),2) + cos(coordsA[0]*0.01745) * cos(coordsB[0]*0.01745) * pow((sin((double)dlon/(double)2*0.01745)),2);
   double c = 2 * atan2(sqrt(aa), sqrt(1-aa));
   double d = 6371 * c; 
   return d;
}

int main() {
   double Vilnius[] = {54.683, 25.317};
   double Kaunas[] = {54.897, 23.886};
   cout << HaversineDistance(Vilnius, Kaunas) << endl;
}