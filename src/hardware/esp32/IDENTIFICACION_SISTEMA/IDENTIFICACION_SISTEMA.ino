// Autor: Ruben Sahuquillo Redondo
// Master Informatica Industrial y Robotica

// LIBRERIAS
#include <Adafruit_MAX31856.h>

// PINES
#define DRDY_PIN 4
#define CS_PIN 5
#define RELE 22

// ESTADOS DEL INSTRUMENTO
enum Estado {
  INICIO,
  CONFIG,
  PARADA
};
Estado estadoActual = PARADA;

// VARIABLES TEMPERATURAS
float temperatura = 0.00;
float temperatura_maxima = 300.00;

// VARIABLES DE TIEMPOS
float tiempo = 0.00;
unsigned long tiempo_actual = 0;
unsigned long tiempo_anterior = 0;
unsigned long tiempo_inicial= 0;

// VARIABLES DE PWM
int pwm = 0;
unsigned long ventana_pwm = 2000;
unsigned long inicio_ventana = 0;

// OBJETOS
Adafruit_MAX31856 maxthermo = Adafruit_MAX31856(CS_PIN);

// FUNCION INICIAR INSTRUMENTO
void iniciar_instrumento(){
  // Configurar pines
  pinMode(DRDY_PIN, INPUT);
  pinMode(RELE, OUTPUT);
  // Configurar termopar
  if (!maxthermo.begin()) {
    while (true){
      delay(10);
    }
  }
  maxthermo.setThermocoupleType(MAX31856_TCTYPE_K);
  maxthermo.setConversionMode(MAX31856_CONTINUOUS);
}

// FUNCION CONFIGURAR INSTRUMENTO
void configurar_instrumento(){
  while (Serial.available() == 0) {
    delay(10);
  }
  temperatura_maxima = Serial.parseFloat();
  pwm = Serial.parseInt();
  Serial.println("OK");
}

// FUNCION CONTROL RELE
void pwm_rele(int pct_pwm) {
  unsigned long tiempoEncendido = (pct_pwm * ventana_pwm) / 100;
  unsigned long tiempoActualCiclo = millis() - inicio_ventana;
  // Reiniciar ventana de 1 segundo
  if (tiempoActualCiclo >= ventana_pwm) {
    inicio_ventana = millis();
  }
  // Si pct_pwm > 0 y no ha terminado la ventana de pwm
  if ((pct_pwm > 0) && (tiempoActualCiclo < tiempoEncendido)) {
    digitalWrite(RELE, HIGH);
  // Si pct_pwm == 0 o ha terminado la ventana de pwm
  } else {
    digitalWrite(RELE, LOW);
  }
}

// FUNCION PARA LEER TEMPERATURA
float leer_temperatura() {
  int count = 0;
  while (digitalRead(DRDY_PIN)) {
    if (count++ > 200) {
      count = 0;
    }
  }
  return maxthermo.readThermocoupleTemperature();
}

// FUNCION ADQUISICION
void adquisicion() {
  tiempo_actual = millis();
  if ((tiempo_actual - tiempo_anterior) >= 1000) {
    temperatura = leer_temperatura();
    float tiempo_relativo = (tiempo_actual - tiempo_inicial) / 1000.0;
    Serial.print(tiempo_relativo, 2);
    Serial.print(",");
    Serial.println(temperatura, 2);
    tiempo_anterior = tiempo_actual;
  }
}

// FUNCION SETUP()
void setup() {
  // Iniciar puerto serie
  Serial.begin(115200);
  while (!Serial){
    delay(10);
  }
  // Iniciar instrumento
  iniciar_instrumento();
  tiempo_anterior = millis();
  tiempo_inicial = millis();
}

// FUNCION LOOP()
void loop() {
  // Gestion de comunicaciones
  if (Serial.available() > 0) {
    // Leer comando por serial
    String comando = Serial.readStringUntil('\n');
    // Limpiar comando
    comando.trim();
    // Comando recibido
    if (comando == "PARADA"){
        estadoActual = PARADA;
    }
    else if (comando == "CONFIG") {
      estadoActual = CONFIG;
      Serial.println("OK");
    }
    else if (comando == "INICIO") {
      estadoActual = INICIO;
      tiempo_inicial = millis();
    }
  }

  // Ejecucion maquina de estados
  switch (estadoActual) {
    case INICIO:
      // Comprobacion de seguridad
      temperatura = leer_temperatura();
      if (temperatura >= temperatura_maxima) {
        estadoActual = PARADA;
        break;
      }
      pwm_rele(pwm);
      adquisicion();
      break;

    case PARADA:
      digitalWrite(RELE, LOW);
      break;

    case CONFIG:
      digitalWrite(RELE, LOW);
      configurar_instrumento();
      break;
  }
}