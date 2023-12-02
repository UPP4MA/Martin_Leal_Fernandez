// Pines de señales PWM
const int ena = 10;
const int enb = 5;

// Pines de control de dirección
const int in1 = 9;
const int in2 = 8;
const int in3 = 7;
const int in4 = 6;

// Pin del sensor de humedad del suelo
const int sensorHumedadPin = A0;

// Umbral de humedad para considerar que hay agua
const int umbralHumedad = 600;

bool motoresActivados = false;
unsigned long tiempoInicio;

void setup() {
  Serial.begin(9600);
  Serial.println(F("----------------------------------------------------"));
  Serial.println(F("              L298N - CONTROL DE MOTORES            "));
  Serial.println(F("              https://www.geekfactory.mx            "));
  Serial.println(F("----------------------------------------------------"));

  pinMode(ena, OUTPUT);
  pinMode(enb, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);

  digitalWrite(ena, LOW);
  digitalWrite(enb, LOW);
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);

  delay(1000);
}

void loop() {
  int valorHumedad = analogRead(sensorHumedadPin);
  Serial.print(F("H:"));
  Serial.println(valorHumedad); // Envía el valor de humedad por el puerto serial

  if (Serial.available() > 0) {
    char receivedChar = Serial.read();
    if (receivedChar == 'A') {
      motoresActivados = true; // Activa los motores al recibir 'A' desde Python
      tiempoInicio = millis(); // Guarda el tiempo actual
    } else if (receivedChar == 'D') {
      motoresActivados = false; // Detiene los motores al recibir 'D' desde Python
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, LOW);
      analogWrite(ena, 0);
      analogWrite(enb, 0);
      Serial.println(F("Motores detenidos"));
    }
  }

  if (motoresActivados) {
    // Activar los motores
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);
    analogWrite(ena, 255);
    analogWrite(enb, 255);
    Serial.println(F("Motores activados"));

    // Verificar si han pasado 15 segundos desde que se activaron los motores
    if (millis() - tiempoInicio >= 15000) {
      // Detener los motores después de 15 segundos
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      digitalWrite(in3, LOW);
      digitalWrite(in4, LOW);
      analogWrite(ena, 0);
      analogWrite(enb, 0);
      Serial.println(F("Motores detenidos"));
      motoresActivados = false;
    }
  }
