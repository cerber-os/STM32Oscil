/*
 * pcCom.c
 * Module providing functions to exchange information with host over USART
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#include "stm32f10x.h"
#include "../inc/pcCom.h"
#include "../inc/queue.h"

// Current state of communication
enum pcComStates pcComCurrentState = NEW_DATA;
// Access global variables declared in queue.c
extern Queue txQueue, rxQueue;

union payload_t payload;

// Get message from host
//		Returns: command represented as in pcComCommands enum
//				 including: WAIT_FOR_DATA - we are still waiting for payload
//							INVALID_COMMAND - host sent unknown command code
int processPcCom(void) {
	unsigned char data;
	static int payloadLength;
	static int payloadBytesReadSoFar = 0;
	static char commandCode = 0;

	if(!isQueueEmpty(&rxQueue)) {
		switch(pcComCurrentState) {
		case NEW_DATA:
			GPIO_WriteBit(GPIOB, GPIO_Pin_8, 1 - GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_8));
			popFromQueue(&rxQueue, (char*)&data);
			commandCode = data;

			if(data == PING || data >= IS_DATA_AVAIL)
				return data;				// This commands does not contain payload
			else if(data > TRIG_NOW)		// Command code is outside pcComCommands enum
				return INVALID_COMMAND;
			else {
				pcComCurrentState = WAIT_FOR_PAYLOAD;
				payloadBytesReadSoFar = 0;
				if(data == SET_SAMPLES || data == SET_TRIGGER || data == SET_PRECISION)
					payloadLength = 4;		// This commands contain 4 byte payload
				else
					payloadLength = 1;		// ... and this 1 byte payload
				payload.dword = 0;
				return WAIT_FOR_DATA;
			}
			break;

		case WAIT_FOR_PAYLOAD:
			popFromQueue(&rxQueue, (char*)&data);

			payload.bytes[payloadBytesReadSoFar] = data;
			payloadBytesReadSoFar++;

			if(payloadBytesReadSoFar >= payloadLength) {
				pcComCurrentState = NEW_DATA;
				return commandCode;
			}
			break;
		}
	}
	return WAIT_FOR_DATA;
}

// Send one byte to host
void sendByte(uint8_t byte) {
	while(pushToQueue(&txQueue, byte) != QUEUE_SUCCESS) ;
	USART_ITConfig(USART1, USART_IT_TXE, ENABLE);
}

// Send operation status to host
void sendAck(uint8_t operationStatus) {
	sendByte(operationStatus);
}

void sendWord(uint16_t data) {
	sendByte(data & 0xff);
	sendByte(data >> 8);
}

void sendDword(uint32_t data) {
	sendWord(data & 0xffff);
	sendWord(data >> 16);
}

// Send samples stored in global samples[] array
void sendProbes(int length, uint16_t* samples) {
	sendDword(length);		// Send number of samples as 4byte value

	for(int i = 0; i < length; i++)
		sendWord((samples[i] * 8059) / 10000);

	sendAck(0xff);			// End of transmission
}
