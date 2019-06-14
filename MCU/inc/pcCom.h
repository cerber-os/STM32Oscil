/*
 * pcCom.h
 * Header file of pcCom.c
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#ifndef PCCOM_H_
#define PCCOM_H_

// Definition of union used to store different size of incoming data
union payload_t {
	char bytes[4];
	int dword;
};

// Definition of enum representing states of transmission
enum pcComStates {NEW_DATA, WAIT_FOR_PAYLOAD};

// Definition of enum representing commands host can send
enum pcComCommands {INVALID_COMMAND = -2, WAIT_FOR_DATA = -1, SET_TRIGGER = 0, SET_MODE,
	PING, SET_SAMPLES, SET_PRECISION, IS_DATA_AVAIL, DOWNLOAD_DATA, TURN_OFF, TRIG_MODE,
	TRIG_NOW};

// Definitions of functions
int processPcCom(void);
void sendAck(uint8_t);
void sendProbes(int length, uint16_t* samples);

#endif /* PCCOM_H_ */
