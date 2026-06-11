/*
 * state_machine.c
 *
 *  Created on: 11 jun 2026
 *      Author: rsahu
 */


#include "state_machine.h"
#include "main.h"
#include <stdio.h>
#include <string.h>


extern UART_HandleTypeDef huart1;


static SystemState_t system_state = SYS_BOOT;
static SystemState_t prev_system_state = SYS_BOOT;


// Metodo para convertir estado en string
static const char* State_ToString(SystemState_t state)
{
    switch (state)
    {
        case SYS_BOOT:
        	return "BOOT";

        case SYS_IDLE:
        	return "IDLE";

        case SYS_MANUAL_CONTROL:
        	return "MANUAL_CONTROL";

        case SYS_AUTO_INIT:
        	return "AUTO_INIT";

        case SYS_AUTO_PREHEAT:
        	return "AUTO_PREHEAT";

        case SYS_AUTO_READY:
        	return "AUTO_READY";

        case SYS_AUTO_EXTRUDING:
        	return "AUTO_EXTRUDING";

        case SYS_STOPPING:
        	return "STOPPING";

        case SYS_ALARM:
        	return "ALARM";

        default:
        	return "UNKNOWN";
    }
}


// Metodo para imprimir estado si este cambia
static void State_PrintIfChanged(void)
{
    char msg[64];

    if (system_state != prev_system_state)
    {
        snprintf(msg, sizeof(msg),
                 "STATE: %s -> %s\r\n",
                 State_ToString(prev_system_state),
                 State_ToString(system_state));

        HAL_UART_Transmit(&huart1, (uint8_t*)msg, strlen(msg), 100);
    }
}


// Metodo para inicializar la maquina de estados
void StateMachine_Init(void)
{
	system_state = SYS_BOOT;
	prev_system_state = SYS_BOOT;

}


// Metodo para gestionar la maquina de estados
void StateMachine_Control(uint32_t now, AppCommands_t *cmd, AppData_t *data, AppConfig_t *config)
{

	if (cmd->alarm_cmd)
	{
		cmd->alarm_cmd = 0;
		system_state = SYS_ALARM;
	}

	switch (system_state)
	{
		case SYS_BOOT:
			/*
			 *  BOOT -> IDLE si init_ok
			 *  BOOT -> ALARM si falla init
			 *  */
			if (data->init_ok)
			{
				system_state = SYS_IDLE;
			}
			break;

		case SYS_IDLE:
            /*
             * IDLE -> MANUAL_CONTROL con set_manual_cmd
             * IDLE -> AUTO_INIT con set_auto_cmd
             */
			if (cmd->set_manual_cmd)
			{
				cmd->set_manual_cmd = 0;
				system_state = SYS_MANUAL_CONTROL;
			}
			if (cmd->set_auto_cmd)
			{
				cmd->set_auto_cmd = 0;
				system_state = SYS_AUTO_INIT;
			}
			break;

		case SYS_MANUAL_CONTROL:
            /*
             * MANUAL_CONTROL -> STOPPING con stop_cmd
             * MANUAL_CONTROL -> AUTO_INIT con set_auto_cmd
             */
            if (cmd->stop_cmd)
            {
                cmd->stop_cmd = 0;
                system_state = SYS_STOPPING;
            }
            else if (cmd->set_auto_cmd)
            {
                cmd->set_auto_cmd = 0;
                system_state = SYS_AUTO_INIT;
            }
            break;

		case SYS_AUTO_INIT:
            /*
             * AUTO_INIT -> AUTO_PREHEAT si init_auto_ok
             * AUTO_INIT -> IDLE si reset_auto_cmd
             */
            if (cmd->reset_auto_cmd)
            {
                cmd->reset_auto_cmd = 0;
                system_state = SYS_IDLE;
            }
            else if (data->init_auto_ok || cmd->init_auto_ok)
            {
                system_state = SYS_AUTO_PREHEAT;
            }
            break;

		case SYS_AUTO_PREHEAT:
            /*
             * AUTO_PREHEAT -> AUTO_READY si temperature_ok
             * AUTO_PREHEAT -> STOPPING con stop_cmd
             */
            if (cmd->stop_cmd)
            {
                cmd->stop_cmd = 0;
                system_state = SYS_STOPPING;
            }
            else if (data->temperature_ok || cmd->temperature_ok)
            {
                system_state = SYS_AUTO_READY;
            }
            break;

		case SYS_AUTO_READY:
            /*
             * AUTO_READY -> AUTO_EXTRUDING si extrude_ok
             * AUTO_READY -> STOPPING con stop_cmd
             */
            if (cmd->stop_cmd)
            {
                cmd->stop_cmd = 0;
                system_state = SYS_STOPPING;
            }
            else if (data->extrude_ok || cmd->extrude_ok)
            {
                system_state = SYS_AUTO_EXTRUDING;
            }
            break;

		case SYS_AUTO_EXTRUDING:
            /*
             * AUTO_EXTRUDING -> STOPPING con stop_cmd
             */
            if (cmd->stop_cmd)
            {
                cmd->stop_cmd = 0;
                system_state = SYS_STOPPING;
            }
            break;

		case SYS_STOPPING:
            /*
             * STOPPING -> IDLE si outputs_ok
             */
            if (data->outputs_ok || data->stop_ok || cmd->outputs_ok || cmd->stop_ok)
            {
                system_state = SYS_IDLE;
            }
            break;

		case SYS_ALARM:
            /*
             * ALARM -> IDLE con reset_alarm_cmd e init_ok
             */
            if (cmd->reset_alarm_cmd && (data->init_ok || cmd->init_ok))
            {
                cmd->reset_alarm_cmd = 0;
                system_state = SYS_IDLE;
            }
            break;

        default:
            system_state = SYS_ALARM;
            break;
    }


	if (config->debug_enabled)
	{
	    State_PrintIfChanged();
	}

	prev_system_state = system_state;
}
