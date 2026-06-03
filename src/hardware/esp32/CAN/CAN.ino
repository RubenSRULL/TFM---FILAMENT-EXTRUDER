#include "driver/twai.h"

#define CAN_TX_PIN GPIO_NUM_5
#define CAN_RX_PIN GPIO_NUM_4

void setup() {
    Serial.begin(115200);

    twai_general_config_t g_config = TWAI_GENERAL_CONFIG_DEFAULT(CAN_TX_PIN, CAN_RX_PIN, TWAI_MODE_NORMAL);
    twai_timing_config_t t_config = TWAI_TIMING_CONFIG_500KBITS();
    twai_filter_config_t f_config = TWAI_FILTER_CONFIG_ACCEPT_ALL();

    if (twai_driver_install(&g_config, &t_config, &f_config) == ESP_OK && twai_start() == ESP_OK) {
        Serial.println(">>> Monitor CAN Multicanal Iniciado");
    }
}

void loop() {
    twai_message_t rx_msg;

    // Esperar cualquier mensaje en el bus
    if (twai_receive(&rx_msg, pdMS_TO_TICKS(100)) == ESP_OK) {
        
        // 1. Convertir datos a String
        String mensaje = "";
        for (int i = 0; i < rx_msg.data_length_code; i++) {
            mensaje += (char)rx_msg.data[i];
        }


        // 2. Identificar procedencia y actuar
        if (rx_msg.identifier != 0x300) {

            Serial.print("ID Recibido: 0x");
            Serial.print(rx_msg.identifier, HEX);
            Serial.print(" | Contenido: ");
            Serial.println(mensaje);

            switch (rx_msg.identifier) {
                case 0x100: // Ejemplo: Control de Temperatura
                    Serial.println("Acción: Ajustando Calefactor...");
                    enviarString(0x300, "OK"); // Respondemos al mismo ID para confirmar
                    break;

                case 0x101: // Ejemplo: Extrusora
                    Serial.println("Acción: Comandando Extrusora...");
                    enviarString(0x300, "OK");
                    break;

                case 0x102: // Ejemplo: Enrolladora
                    Serial.println("Acción: Comandando Enrolladora...");
                    enviarString(0x300, "OK");
                    break;

                default:
                    Serial.println("ID desconocido, no se requiere respuesta.");
                    break;
            }
        }
    }
}

// Función genérica de envío
void enviarString(uint32_t id, String texto) {
    twai_message_t tx_msg;
    tx_msg.identifier = id;
    tx_msg.extd = 0;
    int len = texto.length();
    if (len > 8) len = 8;
    tx_msg.data_length_code = len;

    for (int i = 0; i < len; i++) {
        tx_msg.data[i] = texto[i];
    }

    twai_transmit(&tx_msg, pdMS_TO_TICKS(100));
}