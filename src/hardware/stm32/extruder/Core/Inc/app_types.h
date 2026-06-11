/*
 * app_types.h
 *
 *  Created on: 11 jun 2026
 *      Author: rsahu
 */


#ifndef INC_APP_TYPES_H_
#define INC_APP_TYPES_H_


#include <stdint.h>


typedef enum
{
	SYS_BOOT = 0,
	SYS_IDLE,
	SYS_MANUAL_CONTROL,
	SYS_AUTO_INIT,
	SYS_AUTO_PREHEAT,
	SYS_AUTO_READY,
	SYS_AUTO_EXTRUDING,
	SYS_STOPPING,
	SYS_ALARM
} SystemState_t;


typedef struct
{
	uint8_t set_manual_cmd;
	uint8_t set_auto_cmd;
	uint8_t reset_auto_cmd;
	uint8_t stop_cmd;
	uint8_t reset_alarm_cmd;
	uint8_t alarm_cmd;
	uint8_t init_ok;
	uint8_t init_auto_ok;
	uint8_t temperature_ok;
	uint8_t extrude_ok;
	uint8_t stop_ok;
	uint8_t outputs_ok;
} AppCommands_t;


typedef struct
{
	uint8_t init_ok;
	uint8_t init_auto_ok;
	uint8_t temperature_ok;
	uint8_t extrude_ok;
	uint8_t stop_ok;
	uint8_t outputs_ok;
} AppData_t;


typedef struct
{
    uint8_t debug_enabled;
} AppConfig_t;


#endif /* INC_APP_TYPES_H_ */
