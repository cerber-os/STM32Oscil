/*
 * probe.h
 * Header of file probe.c
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#ifndef PROBE_H_
#define PROBE_H_

// Maximum number of samples that could be taken
#define MAX_NUMBER_OF_SAMPLES		4000

// Enum representing various states of probing
enum probbingStates {OFF, WAITING_FOR_TRIG, WORKING, FINISHED};

// Definitions of functions
int setMaxNumberOfSamples(int);
int setProbingMode(int);
int setTriggerLevel(int);
int setFreq(uint32_t);
void printState(void);
int triggerNow(void);
int setOff(void);
int setTrigMode(void);
void SysTick_Handler(void);

#endif /* PROBE_H_ */
