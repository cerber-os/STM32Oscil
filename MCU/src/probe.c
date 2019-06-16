/*
 * probe.c
 * Module providing probing capabilities of device
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#include <stdio.h>
#include "stm32f10x.h"
#include "../inc/probe.h"
#include "../inc/hd44780.h"

// Global array, where taken samples will be stored
uint16_t samples[MAX_NUMBER_OF_SAMPLES + 1];
// Variable indicating how many samples has already been taken
uint16_t currentNumberOfSamples = 0;
// Current state of probing
uint8_t state = OFF;
// Frequency at which samples should be taken
uint32_t currentFreq = 1000;

// The number of samples to be taken - value set by host
int maxNumberOfSamples = 0;
// Current probing mode - not implemented yet
int probingMode = 0;
// Value at which probing will be automatically started if in WAITING_FOR_TRIG state
int triggerLevel = 0;

// Set number of samples to be taken
// 		Returns: 0 on success, 1 if value is invalid, 2 if device is currently taking samples
int setMaxNumberOfSamples(int no) {
	if(no > MAX_NUMBER_OF_SAMPLES || no < 0)
		return 1;
	if(state == WORKING)
		return 2;

	maxNumberOfSamples = no;
	return 0;
}

// Set probing mode
//		Returns: 0 on success, 2 if device is busy
int setProbingMode(int mode) {
	if(state == WORKING)
		return 2;
	probingMode = mode;
	return 0;
}

// Convert provided level to ADC value and set as new triggerLevel
//		Returns: 0 on success, 1 if argument is invalid, 2 if busy
int setTriggerLevel(int level) {
	if(state == WORKING)
		return 2;
	if(level < 0)
		return 1;
	triggerLevel = (level * 10000) / 8059;
	return 0;
}

// Set frequency of timer used to take sample of signal
int setFreq(uint32_t freq) {
	if(state == WORKING)
		return 2;
	currentFreq = freq;
	if(SysTick_Config(freq))
		return 2;
	return 0;
}

// Trigger probing now
int triggerNow(void) {
	if(state != WORKING) {
		currentNumberOfSamples = 0;
		state = WORKING;
	} else
		return 2;
	return 0;
}

// Disable probing
int setOff(void) {
	state = OFF;
	currentNumberOfSamples = 0;
	return 0;
}

// Enable WAITING_FOR_TRIG state
int setTrigMode(void) {
	if(state != WORKING) {
		currentNumberOfSamples = 0;
		state = WAITING_FOR_TRIG;
	} else
		return 2;
	return 0;
}

// Returns current state of probing
int getState(void) {
	return state;
}

// Prints basic information about probing on 16x2 LCD display
void printState(void) {
	char firstLine[16];
	char secondLine[16];

	char cpProbingMode = '?';
	char cpState;
	// Convert mode to readable format
	if(probingMode == 0)
		cpProbingMode = 'A';
	else if(probingMode == 1)
		cpProbingMode = 'D';

	// Convert state to readable format
	if(state == OFF)
		cpState = '0';
	else if(state == WAITING_FOR_TRIG)
		cpState = 'W';
	else if(state == WORKING)
		cpState = '1';
	else if(state == FINISHED)
		cpState = 'F';
	else
		cpState = '0' + (state % 10);

	snprintf(firstLine, sizeof(firstLine), "M:%c S:%c T:%d", cpProbingMode, cpState, triggerLevel);
	snprintf(secondLine, sizeof(secondLine), "No:%d", maxNumberOfSamples);


	HD44780_Clear();
	HD44780_Puts(0, 0, firstLine);
	HD44780_Puts(0, 1, secondLine);
}

// Hander for SysTick interrupt
void SysTick_Handler(void) {
	if(state == OFF || state == FINISHED) {
		// Do nothing
	} else if(state == WAITING_FOR_TRIG) {
		uint16_t sample = ADC_GetConversionValue(ADC1);
		if(sample <= triggerLevel) {		// We have been triggered
			state = WORKING;
			currentNumberOfSamples = 0;
			samples[currentNumberOfSamples++] = ADC_GetConversionValue(ADC1);
		}
	} else if(state == WORKING) {
		if(currentNumberOfSamples < maxNumberOfSamples)
			samples[currentNumberOfSamples++] = ADC_GetConversionValue(ADC1);
		else					// We have reached expected number of samples
			state = FINISHED;
	}
}
