#include<Stepper.h>
#include<DHT.h>
#include<SPI.h>
#include<SoftwareSerial.h>

//motor-NEMA17 control
int steps = 7;
int dir = 8;
//int ms1 = 9;
//int ms2 = 10;
//int ms3 = 11;

int rain = A0;
int rain_state = 0; //0~1000 lower number->more rain

int gas = A1;
int gas_state = 0; //0~1000 

#define DHTPIN 2    // SDA 핀의 설정
#define DHTTYPE DHT22   // DHT22 (AM2302) 센서종류 설정
DHT dht(DHTPIN, DHTTYPE);
float h = 0; float t = 0; // humidity and temperature

int switch1 = 3;
int switch2 = 4;
int switch1_state, switch2_state = 0;

int full_time = 0;
int hh, mm = 0;

int window23 = 9;
int window23_state = 0;
int window24 = 10;
int window24_state = 0;
int fire = 11;
int fire_camera = 0;

//int d_particle = 12;
//int d_particle_state = 0;
int a_particle = A4;
int a_particle_state = 0;
float particle_voltage = 0;
float particle_density = 0;

SoftwareSerial mySerial3(A3, A2);
//SoftwareSerial mySerial1(4, 3);
//SoftwareSerial mySerial2(6, 5);

void setup() {
  pinMode(rain, INPUT);
  pinMode(gas, INPUT);
  pinMode(window23, INPUT);
  pinMode(window24, INPUT);
  pinMode(fire, INPUT);
  dht.begin();
  pinMode(switch1, INPUT);
  pinMode(switch2, INPUT);
  pinMode(steps, OUTPUT);
  pinMode(dir, OUTPUT);
 // pinMode(d_particle, OUTPUT);
  pinMode(a_particle, INPUT);
  //pinMode(ms1, OUTPUT);
  //pinMode(ms2, OUTPUT);
  //pinMode(ms3, OUTPUT);
//  digitalWrite(ms1, LOW);
 // digitalWrite(ms2, LOW);
  //digitalWrite(ms3, LOW);
  Serial.begin(9600);
//  mySerial1.begin(9600);
//  mySerial2.begin(9600);
  mySerial3.begin(115200);
}

void loop() {
  rain_state = analogRead(rain);
  gas_state = analogRead(gas);
  h = dht.readHumidity();
  t = dht.readTemperature();
  switch1_state = digitalRead(switch1);
  switch2_state = digitalRead(switch2);
  window23_state = digitalRead(window23);
  window24_state = digitalRead(window24);
  fire_camera = digitalRead(fire);
 // d_particle_state = digitalWrite(d_particle);
  a_particle_state = analogRead(a_particle);
  particle_voltage = a_particle_state*5.0 / 1023.0;
  particle_density = (1/6.0)*(particle_voltage-0.6); // dust density calculation, mg/m3

  if(particle_density >= 0.8){
    Serial.println("high particle");
    Serial.println(particle_density);
  }
  else{
    Serial.println("low particle");
    Serial.println(particle_density);
  }
  
  String rain_string = String(int(rain_state));
  String gas_string = String(int(gas_state));
  String h_string = String(int(h));
  String t_string = String(int(t));
  String p_string = String(int(particle_density*1000));
  String total_state = rain_string + ":" + gas_string + ":" + h_string + ":" + t_string + ":" + p_string;
  Serial.println(total_state);
  mySerial3.println(total_state);

 // if(mySerial1.available()>0){
  //  Serial.println("ser1 avarilable");
   // fire_camera = mySerial1.parseInt();
//  }
//  else{
//    Serial.println("ser1 NOT NOT avarilable");
//    fire_camera = 0;
//  }
  
//  if(mySerial2.available()>0){
  //  full_time = mySerial2.parseInt();
   // hh = full_time / 100;
  //  mm = full_time % 100;
//  }
//  else{
//    fire_camera = 0;
//  }
  Serial.println("serial value");
  Serial.println(fire_camera);
  Serial.println(full_time);
  Serial.println(hh);
  Serial.println(mm);
  Serial.println(window23_state);
  Serial.println(window24_state);
  Serial.println(switch1_state);
  Serial.println("serial value");



  if(((gas_state>500) or (fire_camera ==1 )) and (switch2_state==1)){ //gas or fire, then open window
    Serial.println("first");
    digitalWrite(dir, 0);
    for(int i=0; i<64; i++){
         digitalWrite(steps, HIGH);
         delayMicroseconds(5000);
         digitalWrite(steps, LOW);
         delayMicroseconds(5000);
         if(switch2_state==0){break;}
    }
    }
  else if(((window23_state==1) and (window24_state==1)) and (switch2_state==1)){ // user open, then open window
    Serial.println("Second");
    digitalWrite(dir, 0);
    for(int i=0; i<64; i++){
         digitalWrite(steps, HIGH);
         delayMicroseconds(5000);
         digitalWrite(steps, LOW);
         delayMicroseconds(5000);
         if(switch2_state==0){break;}
        }
  }
  else if(((window23_state==1) and (window24_state==0)) and (switch1_state==1)){ //user close, then close window
    Serial.println("third");
    digitalWrite(dir, 1);
    for(int i=0; i<64; i++){
      if(switch1_state==0){break;}
         digitalWrite(steps, HIGH);
         delayMicroseconds(7500);
         digitalWrite(steps, LOW);
         delayMicroseconds(7500);
      if(switch1_state==0){break;}
     }
  }
  else if( ((rain_state<600) or (particle_density>=0.8)) and (switch1_state==1)){ //no user order, and rain, then close window  ///add smog
    Serial.println("fourth");
    digitalWrite(dir, 1);
    for(int i=0; i<64; i++){
         digitalWrite(steps, HIGH);
         delayMicroseconds(7500);
         digitalWrite(steps, LOW);
         delayMicroseconds(7500);
         if(switch1_state==0){break;}
     }
  }


  //else {
    //break;
    //}


    Serial.print("Rain: ");Serial.println(rain_state);
    Serial.print("Gas:");Serial.println(gas_state);
    Serial.print("Humidity: "); Serial.println(h);
    Serial.print("Temperature: "); Serial.println(t);

    delay(1000);
  

}
