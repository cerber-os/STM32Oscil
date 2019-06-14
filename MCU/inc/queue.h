/*
 * queue.h
 * Header file of queue.c
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#ifndef QUEUE_H_
#define QUEUE_H_

// Maximum number of elements queue can handle
#define MAX_QUEUE_SIZE  20

// Return codes
#define QUEUE_SUCCESS	0
#define QUEUE_FULL		1
#define QUEUE_EMPTY		1

// Definition of structure representing queue
struct queue_t {
	char queue[MAX_QUEUE_SIZE];			// array storing byte elements
	int start;							// position at which queue starts
	int end;							// position at which queue ends
};
typedef struct queue_t Queue;

// Functions declarations
void clearQueue(Queue*);
int pushToQueue(Queue*, char);
int popFromQueue(Queue*, char*);
int isQueueEmpty(Queue*);

#endif /* QUEUE_H_ */
