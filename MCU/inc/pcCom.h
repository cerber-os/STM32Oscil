/*
 * pcCom.h
 *
 *  Created on: 09.06.2019
 *      Author: anybody
 */

#ifndef PCCOM_H_
#define PCCOM_H_

union payload_t {
	char bytes[4];
	int dword;
};

enum pcComStates {NEW_DATA, WAIT_FOR_PAYLOAD};
enum pcComCommands {INVALID_COMMAND = -2, WAIT_FOR_DATA = -1, SET_TRIGGER = 0, SET_MODE,
	PING, SET_SAMPLES, SET_PRECISION, IS_DATA_AVAIL, DOWNLOAD_DATA, TURN_OFF, TRIG_MODE,
	TRIG_NOW};

int processPcCom(void);
void sendAck(uint8_t);
void sendProbes(int length, uint16_t* samples);

#endif /* PCCOM_H_ */
