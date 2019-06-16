/*
 * main.c
 *
 *  Created on: 08.06.2019
 *      Author: Paweł Wieczorek
 */
#include "stm32f10x.h"
#include "../inc/hd44780.h"
#include "../inc/pcCom.h"
#include "../inc/queue.h"
#include "../inc/probe.h"

// Local functions definitions
void ConfigRCC(void);
void ConfigNVIC(void);
void ConfigGPIO(void);
void ConfigADC(void);
void ConfigUSART(void);
void USART1_IRQHandler(void);

// Global variable (GV) holding payload of host message
extern union payload_t payload;
// GV holding number of samples already taken
extern uint16_t currentNumberOfSamples;
// Global array contatining samples
extern uint16_t samples[];
// GV containing information about current probing state
extern uint8_t state;
// Global queues used in USART transmission
extern Queue rxQueue, txQueue;

int main(void) {
	ConfigRCC();
	ConfigNVIC();
	ConfigGPIO();
	ConfigADC();
	ConfigUSART();

	if (SysTick_Config(SystemCoreClock / 1000))   // Every millisecond
		while (1)
			;		// Wait for debugger;
	// Turn off LEDs
	GPIO_ResetBits(GPIOB, 0xFF00);

	// Initialize 16x2 LCD and display welcome message
	HD44780_Init(16, 2);
	HD44780_Clear();
	HD44780_Puts(0, 0, "  STM32  Oscil\0");
	HD44780_Puts(2, 1, "PC <-X-> Dev.\0");

	clearQueue(&rxQueue);
	clearQueue(&txQueue);

	// Wait for connection
	while (processPcCom() != PING)
		;
	sendAck(0);

	// Display that we are connected, delay ~1s and print current state
	HD44780_Puts(2, 1, "PC <---> Dev.");
	for (int i = 0; i < 2000000; i++)
		;
	printState();

	for (;;) {
		// Get command from host
		int command = processPcCom();

		// Process command
		switch (command) {
		case SET_TRIGGER:
			sendAck(setTriggerLevel(payload.dword));
			break;
		case SET_MODE:
			sendAck(setProbingMode(payload.dword));
			break;
		case PING:
			sendAck(0);
			break;
		case SET_SAMPLES:
			sendAck(setMaxNumberOfSamples(payload.dword));
			break;
		case TRIG_NOW:
			sendAck(triggerNow());
			break;
		case IS_DATA_AVAIL:
			sendAck(state == FINISHED);
			break;
		case DOWNLOAD_DATA:
			if (state == FINISHED) {		// Check if data is ready
				sendAck(0);
				sendProbes(currentNumberOfSamples, samples);
			} else if (state == WORKING)
				sendAck(2);
			else
				sendAck(1);
			break;
		case TURN_OFF:
			sendAck(setOff());
			break;
		case TRIG_MODE:
			sendAck(setTrigMode());
			break;
		case SET_PRECISION:
			sendAck(setFreq(SystemCoreClock / payload.dword));
			break;
		case WAIT_FOR_DATA:
			// Patiently wait for valid command
			continue;
			break;
		case INVALID_COMMAND:
			sendAck(2);
			continue;
			break;
		}
		// Print state after new command arrives
		printState();
	}
}

void ConfigRCC(void) {
	// Clock configuration is done by System_Init() function.
	// We only need to configure our peripherals

	// Set ADC clock line to 13MHz
	RCC_ADCCLKConfig(RCC_PCLK2_Div6);

	// Enable clock on peripherals
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_ADC1, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_USART1, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOC, ENABLE);
}

void ConfigNVIC(void) {
	NVIC_InitTypeDef NVIC_InitStructure;

	// Set 3 bit for sub priority
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_1);

	// Configure USART1 interrupt
	NVIC_InitStructure.NVIC_IRQChannel = USART1_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0;
	NVIC_Init(&NVIC_InitStructure);
}

void ConfigGPIO(void) {
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;

	// PC4 - ADC input (analog input)
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AIN;
	GPIO_Init(GPIOC, &GPIO_InitStructure);

	// PB8-15 - LED1-8
	GPIO_InitStructure.GPIO_Pin = 0xFF00;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP;
	GPIO_Init(GPIOB, &GPIO_InitStructure);

	// PA9 - USART Tx  (alternative function pull-up)
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_9;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	// PA10 - USART Rx (alternative function floating)
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_10;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
	GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void ConfigADC(void) {
	ADC_InitTypeDef ADC_InitStructure;

	// Set ADC configuration
	ADC_InitStructure.ADC_Mode = ADC_Mode_Independent;
	ADC_InitStructure.ADC_ScanConvMode = DISABLE;
	ADC_InitStructure.ADC_ContinuousConvMode = ENABLE;
	ADC_InitStructure.ADC_ExternalTrigConv = ADC_ExternalTrigConv_None;
	ADC_InitStructure.ADC_DataAlign = ADC_DataAlign_Right;
	ADC_InitStructure.ADC_NbrOfChannel = 1;

	// Init ADC
	ADC_Init(ADC1, &ADC_InitStructure);
	// Select 14th ADC channel and set sample time to 1.5 cycle
	ADC_RegularChannelConfig(ADC1, ADC_Channel_14, 1, ADC_SampleTime_1Cycles5);
	ADC_Cmd(ADC1, ENABLE);

	ADC_ResetCalibration(ADC1);
	// Wait till ADC reset its calibration
	while (ADC_GetResetCalibrationStatus(ADC1))
		;

	ADC_StartCalibration(ADC1);
	// Wait till ADC finish its calibration
	while (ADC_GetCalibrationStatus(ADC1))
		;

	// Start ADC convertsion
	ADC_SoftwareStartConvCmd(ADC1, ENABLE);
}

void ConfigUSART(void) {
	USART_InitTypeDef USART_InitStructure;

	// Set USART1 configuration (38400b/s, no parity, 8b length)
	USART_InitStructure.USART_BaudRate = 38400;
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;
	USART_InitStructure.USART_StopBits = USART_StopBits_1;
	USART_InitStructure.USART_Parity = USART_Parity_No;
	USART_InitStructure.USART_HardwareFlowControl =
			USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;

	USART_Init(USART1, &USART_InitStructure);
	// Enable interrupt on receive buffer change
	USART_ITConfig(USART1, USART_IT_RXNE, ENABLE);
	// Start USART1
	USART_Cmd(USART1, ENABLE);
}

// USART1 interrupt handler
void USART1_IRQHandler(void) {
	if (USART_GetITStatus(USART1, USART_IT_RXNE) != RESET) {
		// There is new data in receive buffer - push it to queue
		if (pushToQueue(&rxQueue, USART_ReceiveData(USART1)) != QUEUE_SUCCESS) {
			// Handle error
		}
	}
	if (USART_GetITStatus(USART1, USART_IT_TXE) != RESET) {
		// USART is ready to send next byte
		if (!isQueueEmpty(&txQueue)) {
			char data;
			popFromQueue(&txQueue, &data);
			USART_SendData(USART1, data);
		} else
			// If no data left, disable interrupt
			USART_ITConfig(USART1, USART_IT_TXE, DISABLE);
	}
}
