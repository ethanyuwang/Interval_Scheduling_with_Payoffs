/* Yuxiang (Ethan) Wang UCSB CS130B PROJ2 */
#include <iostream>
#include <algorithm>
#include <vector>
#include <string>
#include <sstream>
#include <iterator>
using namespace std;
 
/*---------------------------interval structs--------------------------------*/
/* A interval has start time, finish time and payoff */
struct Interval
{
    int start, finish, payoff;
};

/* A utility function prints interval */
void printinterval(Interval j)
{
    cout<<j.start<<" ";
    cout<<j.finish<<" ";
    cout<<j.payoff<<endl;
}
 
/* A utility function that is used for sorting events
   according to finish time */
bool IntervalComparator(Interval s1, Interval s2)
{
    return (s1.finish < s2.finish);
}
 
/*---------------------------actual algorithms--------------------------------*/ 
/* This binary search function finds the lastest interval
   that doesnt confict with current interval
   -1 is returned for failing to find one */
int binarySearch(Interval Intervals[], int index)
{
    /* Initialize 'lo' and 'hi' for Binary Search */
    int lo = 0, hi = index - 1;
 
    /* Perform binary Search iteratively */
    while (lo <= hi)
    {
        int mid = (lo + hi) / 2;
        if (Intervals[mid].finish <= Intervals[index].start)
        {
            if (Intervals[mid + 1].finish <= Intervals[index].start)
                lo = mid + 1;
            else
                return mid;
        }
        else
            hi = mid - 1;
    }
 
    return -1;
}

/* reverse the algorithm to get the actual results */
void BacktrackForSolution(Interval arr[], int resultsIndex[], int table[], int j, int &n)
{
    if(j>=0)
    {
        int pj = binarySearch(arr, j);
        if (arr[j].payoff+table[pj]>=table[j-1])
        {
            printinterval(arr[j]);

            n++;
            resultsIndex[n]=j;
            cout<<"was here 1"<<endl;

            BacktrackForSolution(arr, resultsIndex, table, pj, n);
        }
        else
        {
            BacktrackForSolution(arr, resultsIndex, table, j-1, n);
        }
    }
    else return;
}

/* The main function to find the Max payoff */
void findMaxpayoff(Interval arr[], int n)
{
    /* Sort intervals according to finish time */
    sort(arr, arr+n, IntervalComparator);
 
    /* Create an array to store solutions of subproblems */
    int *table = new int[n];
    table[0] = arr[0].payoff;
 
    /* Fill entries in table[] using recursive property */
    for (int i=1; i<n; i++)
    {
        /* Find payoff including the current interval */
        int inclPay = arr[i].payoff;
        int pjl = binarySearch(arr, i);
        if (pjl != -1)
            inclPay += table[pjl];
 
        /* compare to the payoff without the current interval and then 
           store the maximum payoff in the table*/
        table[i] = max(inclPay, table[i-1]);
    }
 
    /* output maxmium payoff */
    cout<<"Max Payoff: "<<table[n-1]<<endl;

    /* back track of the intervals and store index in resultsIndex */
    int *resultsIndex = new int[n];
    int resultNum = -1;

    int j=n-1;

    while(j>=0)
    {
        int pj = binarySearch(arr, j);
        if (arr[j].payoff+table[pj]>=table[j-1])
        {
            //printinterval(arr[j]);

            resultNum++;
            resultsIndex[resultNum]=j;
            //cout<<"was here 1"<<endl;

            j=pj;
        }
        else
        {
            j--;
        }
    }

    //BacktrackForSolution(arr, resultsIndex, table, n-1, resultNum);
    //resultNum--;

    /* print out intervals in reverse order */
    //cout<<"reverse"<<endl;
    for (; resultNum>=0; resultNum--) printinterval(arr[resultsIndex[resultNum]]);

    delete[] table;
}


 
 /*---------------------------driver program--------------------------------*/ 
int main()
{
    /* assume maximum data size */ 
    int size = 1000000;

    Interval* arr = new Interval[size];

    std::string input;
    int n = 0;
    while(std::getline(std::cin, input))
    {   
        /* parse into tokens */
        vector<string> tokens;
        istringstream iss(input);
        copy(istream_iterator<string>(iss),
            istream_iterator<string>(),
            back_inserter(tokens));
        int start = std::stoi(tokens[0]);
        int finish = std::stoi(tokens[1]);
        int payoff = std::stoi(tokens[2]);
        arr[n]={start,finish,payoff};
        n++;     
    }


    findMaxpayoff(arr, n);
    return 0;
}