---
author: AI Editorial
pubDatetime: 2026-09-12T07:52:28Z
title: "Designing an ESP32-Based Smart RV Security & Gas Leak Alarm System: Integrating MQTT Telemetry, Deep-Sleep Logic, and Fail-Safe Relays"
postSlug: "esp32-smart-rv-gas-leak-security-alarm-mqtt"
featured: false
draft: false
tags:
  - ESP32
  - Smart RV
  - MQTT
  - RV Safety
  - Gas Leak Detector
  - IoT Automation
  - Home Assistant

description: "Comprehensive technical guide for Designing an ESP32-Based Smart RV Security & Gas Leak Alarm System: Integrating MQTT Telemetry, Deep-Sleep Logic, and Fail-Safe Relays."
---

# Akıllı Gaz Kaçağı Tespit Sistemi: ESP32, MQTT ve FreeRTOS ile Güvenli Bir Çözüm

Evlerde ve endüstriyel alanlarda gaz kaçakları, ciddi güvenlik riskleri oluşturabilen felaketlere yol açabilir. Bu makale, ESP32 tabanlı, MQTT protokolü ve FreeRTOS işletim sistemi kullanarak geliştirilmiş, güvenilir ve akıllı bir gaz kaçağı tespit sistemi için kapsamlı bir mühendislik rehberi sunmaktadır. Sistem, gaz kaçağını anında algılayarak solenoid valf aracılığıyla gaz akışını keser ve kullanıcıları bilgilendirir.

## Sistem Mimarisine Genel Bakış

Sistem, ESP32 mikrodenetleyici kartını temel alır ve aşağıdaki ana bileşenlerden oluşur:

*   **Gaz Sensörleri (MQ Serisi):** Ortamdaki gaz yoğunluğunu algılar.
*   **Solenoid Gaz Vanası:** Gaz kaçağı durumunda gaz akışını otomatik olarak keser (Normalde Kapalı - Normally Closed).
*   **MQTT Broker:** Cihazlar arası iletişimi sağlar (örn. Mosquitto, HiveMQ).
*   **Wi-Fi Bağlantısı:** ESP32'nin MQTT broker ile haberleşmesini sağlar.
*   **FreeRTOS:** Paralel görev yönetimi ve gerçek zamanlı işlem yetenekleri sunar.
*   **Güç Yönetimi:** Sistem bileşenlerine istikrarlı güç sağlar.
*   **Kullanıcı Arayüzü/Bildirimler:** Akıllı telefon uygulaması veya web paneli üzerinden durum izleme ve bildirimler.

## Donanım Tasarımı ve Devre Şemaları

### Core Bileşen Seçimi

| Bileşen                 | Model/Özellikler                  | Açıklama                                       |
| :---------------------- | :-------------------------------- | :--------------------------------------------- |
| **Mikrodenetleyici**    | ESP32-WROOM-32                    | Wi-Fi, Bluetooth, Çift Çekirdek, Düşük Güç     |
| **Gaz Sensörü**         | MQ-2 (Yanıcı Gaz)                 | Metan, Propan, Bütan, Hidrojen algılama        |
|                         | MQ-7 (Karbon Monoksit)            | CO algılama                                    |
| **Röle Modülü**         | 5V, Tek Kanallı Röle Modülü       | Solenoid vanayı kontrol eder                   |
| **Solenoid Vana**       | 12V DC, Normalde Kapalı (NC)      | Gaz akışını keser                              |
| **Güç Kaynağı**         | 5V/2A DC Adaptör                  | ESP32 ve çevre birimleri için                  |
|                         | 12V/1A DC Adaptör                 | Solenoid vana için                             |
| **Voltaj Regülatörü**   | LM2596 Buck Konvertör (12V -> 5V) | Solenoid vana güç kaynağından 5V regülasyonu  |
| **LED Göstergeler**     | Kırmızı (Alarm), Yeşil (Normal)   | Durum bildirimi                                |
| **Buzzer**              | Pasif Buzzer                      | Sesli alarm                                    |

### Gaz Sensörü Entegrasyonu ve Kalibrasyonu

MQ serisi gaz sensörleri analog çıkış verir. ESP32'nin Analog-Dijital Dönüştürücüsü (ADC) ile okunur.

*   **ESP32 ADC Özellikleri:** ESP32, 12-bit ADC çözünürlüğüne sahiptir. Bu, 0-4095 arasında değerler alabileceği anlamına gelir. Ancak, doğruluğu ve kararlılığı sağlamak için kalibrasyon gereklidir.
*   **Attenuation (Zayıflama):** Farklı gerilim aralıkları için ADC zayıflaması ayarlanabilir (örn. `ADC_ATTEN_DB_11` ile 0V-3.3V aralığı).
*   **Isıtıcı Direnci (Rs/R0 Oranı):** MQ sensörlerinin hassasiyeti, ısıtıcı direnci (Rh) ve algılama direnci (Rs) arasındaki orana bağlıdır. Sensör veri sayfasından alınan Rs/R0 oranı eğrisi kullanılarak gaz konsantrasyonu (ppm) hesaplanır.

**Örnek Kalibrasyon Adımları:**
1.  Temiz hava ortamında sensörün R0 değerini belirleyin.
2.  Gaz konsantrasyonunu (ppm) Rs/R0 oranına dönüştüren bir denklem veya look-up tablosu oluşturun. Genellikle `ppm = A * (Rs/R0)^B` şeklinde bir güç yasası eğrisi kullanılır.

### Solenoid Vana Kontrolü ve Güvenlik Önlemleri

Solenoid vana, gaz kaçağı durumunda gaz akışını kesmek için kullanılır.

*   **Normalde Kapalı (Normally Closed - NC) Vana:** Enerji verilmediğinde kapalı olan, enerji verildiğinde açılan vanalar güvenlik açısından tercih edilmelidir. Bu, elektrik kesintisi durumunda gaz akışının otomatik olarak kesilmesini sağlar.
*   **Röle Modülü:** ESP32'nin düşük akım çıkışları, solenoid vanayı doğrudan süremez. Bir röle modülü, ESP32'den gelen sinyalle yüksek akım solenoid vanayı kontrol etmek için kullanılır. Röle, ESP32'den izole edilmiş 12V güç kaynağı ile beslenen vanayı açıp kapar.
*   **Flyback Diyot:** Röle veya solenoid gibi indüktif yükleri sürerken, geri EMF'yi (Elektromotor Kuvvet) absorbe etmek ve ESP32'yi korumak için diyot kullanılmalıdır.

### Güç Yönetimi ve Gürültü Filtreleme

Stabil ve temiz bir güç kaynağı, sensör okumalarının doğruluğu ve sistemin güvenilirliği için kritik öneme sahiptir.

*   **Voltaj Regülatörleri:** ESP32 için 3.3V, röle ve solenoid için 12V sağlamak üzere uygun voltaj regülatörleri (örn. LM2596 buck konvertör) kullanılmalıdır.
*   **Kapasitörler:** Giriş ve çıkışta bypass ve filtreleme kapasitörleri, güç hattındaki gürültüyü azaltır ve ani akım çekişlerini dengeleyerek sistem kararlılığını artırır.

**Hesaplama Örneği (Kapasitör Boyutlandırma):**
100kHz anahtarlama frekansında 100mV'lik bir tepe-tepe dalgalanma gerilimi ve 1A'lik bir yük akımı için, çıkış kapasitörü C_out = I_load / (8 * f_sw * V_ripple) formülüyle tahmin edilebilir. Eğer I_load = 1A, f_sw = 100kHz, V_ripple = 0.1V ise, C_out = 1A / (8 * 100000Hz * 0.1V) = 125uF bulunur. 220uF'lik bir kapasitör yeterli marj sağlayacaktır.

## Yazılım Geliştirme ve FreeRTOS Entegrasyonu

ESP32'nin çift çekirdekli yapısı ve FreeRTOS desteği, sistemin farklı görevleri paralel ve gerçek zamanlı olarak yürütmesini sağlar.

### FreeRTOS Görev Yönetimi

FreeRTOS, sistemin temel işlevlerini ayrı görevlere bölerek yönetir:

*   **Gaz Sensörü Okuma Görevi (Core 0):** Belirli aralıklarla (örn. her 1 saniyede) gaz sensörlerinden analog değerleri okur, kalibrasyon algoritmalarını uygulayarak ppm değerini hesaplar. Yüksek öncelikli bir görev olmalıdır.
*   **MQTT İletişim Görevi (Core 1):** Sensör verilerini MQTT broker'a yayınlar ve komutları (örn. vanayı manuel açma/kapama) dinler. Ağ bağlantısı yönetimi de bu görevde yapılabilir.
*   **Alarm Yönetimi Görevi (Core 0/1):** Hesaplanan gaz ppm değeri belirli bir eşiği aştığında alarm durumunu tetikler (buzzer, LED'ler) ve solenoid vanayı kapatma komutunu gönderir.
*   **Deep-Sleep Yönetimi (ULP İşlemci):** Düşük güç modunda, ULP işlemci belirli aralıklarla sensörleri kontrol eder. Eğer bir gaz kaçağı tespit edilirse, ana ESP32'yi uyandırır. Bu, pil ömrünü uzatmak için kritiktir.

### MQTT Protokolü ve Güvenlik

MQTT, IoT cihazları için hafif ve verimli bir mesajlaşma protokolüdür.

*   **Konular (Topics):** Sensör verileri için `home/gas_detector/sensor/mq2_ppm`, `home/gas_detector/sensor/mq7_ppm` gibi konular; kontrol komutları için `home/gas_detector/cmd/solenoid_valve` gibi konular kullanılabilir.
*   **QoS (Quality of Service):** Mesajların teslimat garantisi için QoS seviyeleri (0, 1, 2) kullanılabilir. Alarm mesajları için QoS 1 veya 2 tercih edilmelidir.
*   **Güvenlik:** TLS/SSL ile MQTT bağlantısını şifrelemek ve kullanıcı adı/parola kimlik doğrulaması kullanmak, sistemin güvenliğini artırır.

### Gaz Algılama ve Alarm Mantığı

1.  **Sensör Verisi Toplama:** Gaz sensörlerinden sürekli veri okunur.
2.  **Eşik Değer Karşılaştırması:** Okunan ppm değeri önceden belirlenmiş güvenli eşik değerlerle karşılaştırılır (örn. Metan için 500 ppm).
3.  **Alarm Tetikleme:** Eğer gaz konsantrasyonu eşik değeri aşarsa:
    *   Solenoid vana kapatılır (röle aracılığıyla).
    *   Kırmızı LED yanar, buzzer çalar.
    *   MQTT üzerinden alarm mesajı yayınlanır (`home/gas_detector/status/alarm: ON`).
    *   Kullanıcıya bildirim gönderilir (mobil uygulama, e-posta, SMS).
4.  **Alarm Sıfırlama:** Gaz seviyesi güvenli seviyenin altına düştüğünde veya manuel müdahale ile alarm sıfırlanabilir.

### Düşük Güç Modu (Deep-Sleep)

ESP32'nin Deep-Sleep modu, pil ile çalışan uygulamalar için enerji tasarrufu sağlar.

*   **ULP (Ultra Low Power) İşlemci:** ESP32'nin ULP işlemcisi, ana işlemci uyurken bile belirli görevleri (örn. sensör okuma) düşük güç tüketimiyle yapabilir.
*   **Deep-Sleep Döngüsü:** Sistem, belirli aralıklarla (örn. her 5 dakikada bir) Deep-Sleep moduna girer. ULP işlemci bu süreçte gaz seviyesini izler. Eğer eşik değer aşılırsa, ULP işlemci ana ESP32'yi uyandırır ve alarm prosedürü başlar.

## Geliştirme Ortamı ve Araçlar

*   **PlatformIO IDE veya ESP-IDF:** ESP32 geliştirme için önerilen ortamlardır. FreeRTOS entegrasyonu ve kütüphane yönetimi PlatformIO'da daha kolaydır. ESP-IDF ise daha düşük seviye kontrol sağlar.
*   **Arduino IDE (Opsiyonel):** Daha basit projeler için kullanılabilir ancak FreeRTOS'un tüm özelliklerine erişim kısıtlı olabilir.
*   **MQTT Client Araçları:** MQTT Explorer, Mosquitto_sub/pub gibi araçlar, MQTT mesajlarını izlemek ve hata ayıklamak için faydalıdır.

## Test ve Doğrulama

Sistemin güvenilirliği, kapsamlı testlerle sağlanmalıdır.

*   **Fonksiyonel Testler:** Gaz kaçağı senaryolarını simüle ederek solenoid vananın doğru çalışıp çalışmadığını, alarmların tetiklenip tetiklenmediğini kontrol edin.
*   **Performans Testleri:** Sensör okuma doğruluğunu, MQTT gecikmesini ve sistemin genel tepki süresini ölçün.
*   **Güç Tüketimi Testleri:** Özellikle Deep-Sleep modunda pil ömrünü tahmin etmek için güç tüketimini izleyin.
*   **Güvenlik Testleri:** MQTT bağlantısının şifrelenip şifrelenmediğini ve yetkisiz erişime karşı dayanıklılığını kontrol edin.

## Sonuç

Bu makalede sunulan ESP32 tabanlı akıllı gaz kaçağı tespit sistemi, modern IoT teknolojilerini kullanarak evlerde ve iş yerlerinde gaz güvenliğini artırmak için güçlü bir çözüm sunmaktadır. FreeRTOS'un gerçek zamanlı yetenekleri, MQTT'nin esnek iletişimi ve dikkatli donanım tasarımı sayesinde, sistem güvenilir, verimli ve ölçeklenebilir bir yapıya sahiptir. Bu rehber, benzer güvenlik odaklı IoT projeleri geliştiren mühendisler ve hobi meraklıları için sağlam bir temel oluşturmaktadır.
