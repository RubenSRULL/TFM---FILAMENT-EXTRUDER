/*
 * state_machine.h
 *
 *  Created on: 11 jun 2026
 *      Author: rsahu
 */


#ifndef INC_STATE_MACHINE_H_
#define INC_STATE_MACHINE_H_


#include <stdint.h>
#include "app_types.h"


void StateMachine_Init(void);
void StateMachine_Control(uint32_t now, AppCommands_t *cmd, AppData_t *data, AppConfig_t *config);


#endif /* INC_STATE_MACHINE_H_ */
