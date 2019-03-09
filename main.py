from lexer import lex
from parser import parse

test = '''
int MEGACONSTANT;
float HYPERCONSTANT;
float PI;

int MEGAFUNCTION ( void )
{
    while(x+3 + (3 - 3) + 3 + 3){

}
    return 4; }

int MEGAFUNCTIONTWO(int x,int y){if (x < 0) return x + y; else return x - y;}
float a(float b) {
    int c;
    int x[10];
    if (b < 0){ return 0.0;}
    while (c * (4 + b + MEGACONSTANT * 5)){
        float x;
        x = 3.3333E+19;
        if(x == y){
        int x;
        x = x - 3 + (4 / 3.0);
        }
    }

    x[0] = x[4.4] + x[5.05E-22];


}

// don't parse this

/*

this /*

either */

*/

int gcd( int u, int v) {
if (v == 0) return u;
else return gcd(v,u-u/v*v);

}

void main(void){
int x; int y;
x = input(); y = input();
output(gcd(x,y));
}

int x[10];

int minloc (int a[], int low, int high )
{ int i; int x; int k;
k = low;
x = a[low];
i = low + 1;
while (i < high){
if (a[i] = x)
{
x = a[i];
k = i; }
i = i + 1;
}
return k;
}
'''

test2 = '''
/*/* does some bullshit */
MEGA_SYNTAX_ERROR */

int MEGAFUNCTION ( void )
{

    return 4; }

int MEGAFUNCTIONTWO(int x,int y){if (x < 0) return x + y; else return x - y;}
float a(float b) { // MEGA_SYNTAX_ERROR 2
    if (b < 0) return 0.0;
    while (c * (4 + b + MEGACONSTANT * 5) <= 3E19 / (7 + a(3E-4 + (3 / 7 + (MEGAFUNCTION() + 
    MEGAFUNCTIONTWO(3, 4E4))))+2)) {
        while(0)return 4;
        if (c < 0) {
            if (b < 0)
                return 1;
        }
        else {
            c = c + 2;
        }
    };
    ;;;;
    return MEGACONSTANT + 3E+9;
}

int main(void){int x;
    int y[4];
    x = 4;
    y[0] = 4.0E+0;
    y[1] = MEGAFUNCTIONTWO(x+xx,xx+(xx*MEGAFUNCTION()));
    y[2] = MEGAFUNCTION() + a(y[1]);
    y[1 + (1 * MEGAFUNCTION()) - MEGAFUNCTIONTWO(0, 0.0)] = 17;
    return y[0] + (y[1] + y[2]);
}
'''

parse(lex(test2))
