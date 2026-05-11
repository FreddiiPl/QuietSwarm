#include "julianDate.h"
#include <stdio.h>
#include <time.h>

double currentJulianDateTime(const char *UT1)
{
    struct tm tm_time = {0};

    char *UT1_time = strptime(UT1, "%Y-%m-%d %H:%M:%S", &tm_time);

    if (UT1_time == NULL) {
        printf("Error: Could not interpret datetime string.\n");
        return 1.0;
    }

    long long year  = tm_time.tm_year + 1900;
    long long month = tm_time.tm_mon + 1;
    long long day   = tm_time.tm_mday;
    double hour  = tm_time.tm_hour;
    double minute = tm_time.tm_min;
    double second = tm_time.tm_sec;
    double frac_day = (hour + minute / 60.0 + second / 3600.0) / 24.0;

    if (month <= 2) {
        year -= 1;
        month +=12;
    }

    long long century = year / 100;
    long long gregorian_leap_correction = 2 - century + century / 4;


    double Julian_Date     = 
            (long long) (365.25 * (year + 4716)) 
            +(long long) (30.6001 * (month + 1))
            + day 
            + gregorian_leap_correction
            - 1524.5
            + frac_day;


    double Julian_Date_ref = Julian_Date * SECONDS_PER_DAY;


    return Julian_Date_ref;
}