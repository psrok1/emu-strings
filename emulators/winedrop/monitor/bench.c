#include <time.h>

unsigned int startTime = 0;
unsigned int lastTime = 0;
unsigned int lastCycles = 0;

int currentTime()
{
    // Calling time() many times is much too slow for FInterrupt
    int cycles;
    asm("rdtsc; mov %%edx, %0":"=r"(cycles)::"%edx", "%eax");
    if(lastTime == 0 || cycles != lastCycles)
    {
        lastTime = time(NULL);
        lastCycles = cycles;
    }
    return lastTime;
}

int timeElapsed()
{
    if(!startTime)
        startTime = currentTime();
    return currentTime() - startTime;
}