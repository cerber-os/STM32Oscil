/*
 * queue.c
 * Implementation of queues used in project
 *
 *  Created on: 09.06.2019
 *      Author: Paweł Wieczorek
 */

#include "../inc/queue.h"

Queue rxQueue;					// Global queue used to store data received via USART
Queue txQueue;					// Global queue containing data to be send via USART

void clearQueue(Queue* q) {
	q->start = q->end = 0;
}

// Pushes provided element to queue
//		Returns: QUEUE_SUCCESS or QUEUE_FULL
int pushToQueue(Queue* q, char element) {
	if(q->start != (q->end + 1) % MAX_QUEUE_SIZE) {
		q->queue[q->end] = element;
		q->end = (q->end + 1) % MAX_QUEUE_SIZE;
	} else
		return QUEUE_FULL;
	return QUEUE_SUCCESS;
}

// Removes element from queue and save to provided address
//		Returns: QUEUE_SUCCESS or EMPTY
int popFromQueue(Queue* q, char* element) {
	if(q->start != q->end) {
		*element = q->queue[q->start];
		q->start = (q->start + 1) % MAX_QUEUE_SIZE;
	} else
		return QUEUE_EMPTY;
	return QUEUE_SUCCESS;
}

// Checks if queue is empty
//		Returns: false (0) or true (!= 0)
int isQueueEmpty(Queue* q) {
	return q->start == q->end;
}
