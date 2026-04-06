# Aura Smart Home Systems: Official Technical Manual (v2.4)

## 1. Product: Aura Sentinel Smart Camera
The Aura Sentinel is a high-definition indoor/outdoor security camera with night vision and two-way audio.

### 1.1 LED Status Indicators
* **Solid Blue:** Device is powered on and connected to Wi-Fi.
* **Blinking Blue:** Device is in pairing mode and ready for setup.
* **Solid Red:** Camera is actively recording or a live-stream is being viewed.
* **Blinking Red:** Error state. The camera has lost Wi-Fi connection.
* **No Light:** Device is powered off or receiving insufficient power.

### 1.2 Common Error Codes & Troubleshooting
* **Error C-101 (Authentication Failed):** The Wi-Fi password entered during setup is incorrect. 
  * *Fix:* Hold the reset button on the back of the camera for 10 seconds until you hear a beep, then restart the setup process in the Aura app.
* **Error C-202 (Cloud Sync Failure):** The camera cannot upload footage to the Aura Cloud.
  * *Fix:* Ensure your router's firewall is not blocking port 443. Check your Aura subscription status, as free tiers do not include cloud recording.
* **Error C-505 (Thermal Override):** The camera has exceeded safe operating temperatures (above 45°C / 113°F). 
  * *Fix:* The camera will automatically shut down. Move the camera to a shaded area and wait 30 minutes before powering it back on.

---

## 2. Product: Aura Climate Node (Smart Thermostat)
The Climate Node provides AI-driven temperature control to optimize energy efficiency.

### 2.1 Installation Warnings
* **WARNING:** The Climate Node requires a standard C-Wire (Common Wire) providing 24VAC power. If your home does not have a C-Wire, you MUST purchase the Aura Power Adapter Kit separately. Installing without a C-Wire or Adapter Kit will permanently damage the thermostat's internal battery.

### 2.2 Common Error Codes & Troubleshooting
* **Error T-01 (Sensor Disconnect):** The main unit has lost connection with a remote room sensor.
  * *Fix:* Replace the CR2032 battery in the remote room sensor.
* **Error T-88 (Short Cycle Prevention):** The screen displays a lock icon.
  * *Fix:* This is normal. To protect your HVAC compressor, the Climate Node enforces a 5-minute delay between heating/cooling cycles. Please wait 5 minutes.

---

## 3. Aura Corporate Policies

### 3.1 Standard Warranty
All Aura Smart Home devices come with a standard 1-year limited hardware warranty covering manufacturing defects. Water damage is strictly excluded unless the device is specifically rated IP67 (e.g., the Aura Sentinel Outdoor enclosure).

### 3.2 Subscription Tiers
* **Aura Basic (Free):** Live viewing, thermostat control, local SD card storage up to 32GB.
* **Aura Secure ($9.99/month):** Adds 30-day cloud video history, facial recognition alerts, and advanced HVAC energy reports.

### 3.3 Contacting Human Support
If troubleshooting fails, customers can escalate to a human agent by emailing `support@aurasmart.com`. Please include the device Serial Number and the specific Error Code in the subject line.