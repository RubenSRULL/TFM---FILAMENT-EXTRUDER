/*
 * app.c
 *
 *  Created on: 11 jun 2026
 *      Author: rsahu
 */


#include "app.h"
#include "main.h"
#include "app_types.h"
#include "state_machine.h"


AppCommands_t app_cmd;
AppData_t app_data;
AppConfig_t app_config;


// Iniciar app
void App_Init(uint8_t debug)
{
	app_cmd.set_manual_cmd = 0;
	app_cmd.set_auto_cmd = 0;
	app_cmd.reset_auto_cmd = 0;
	app_cmd.stop_cmd = 0;
	app_cmd.reset_alarm_cmd = 0;
	app_cmd.alarm_cmd = 0;

	app_data.init_ok = 1;
	app_data.init_auto_ok = 0;
	app_data.temperature_ok = 0;
	app_data.extrude_ok = 0;
	app_data.stop_ok = 0;
	app_data.outputs_ok = 1;

	app_config.debug_enabled = debug;

	StateMachine_Init();
}


// Control app
void App_Loop(void)
{
	// Tiempo actual bucle
	uint32_t now = HAL_GetTick();

	// Recepcion de mensajes / eventos
	// PE
	// CAN
	// Temperatura
	// Hall

	// Control Estados
	StateMachine_Control(now, &app_cmd, &app_data, &app_config);

	// Acciones
	// Control Temperatura
	// Control Diametro
	// Control Motor Extrusora
	// Control Motor Enrrolladora

	// Salidas no vitales
	// Debug
	// Pantalla OLED
}
