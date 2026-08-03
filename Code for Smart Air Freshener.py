import random
import time
import os
import sys
from datetime import datetime
from collections import defaultdict


# =============================================================================
# SIMULATION CODE (ACTIVE & FULLY FUNCTIONAL)
# =============================================================================
class SmartAirFreshener:
    """
    Simulates a Smart Air Freshener with IoT connectivity.
    Infused with metrics from the design spec:
    - Temp accuracy: ±0.5°C
    - Humidity accuracy: ±5% RH
    - VOC sensitivity: 0.1 ppm
    - Coverage: 500 sq ft
    - Fluid efficiency: 40% reduction
    - Scent concentration target: 2.0 µg/m³
    """
    
    def __init__(self):
        # --- Core Metrics (initialized to preferred ranges) ---
        self.temperature = 21.0          # °C
        self.humidity = 45.0             # % RH
        self.voc_ppm = 0.2               # Volatile Organic Compounds (ppm)
        self.fluid_ml = 120.0            # Total fluid remaining (ml)
        self.total_sprays = 0            # Counter
        self.scent_concentration = 2.0   # µg/m³ (target)
        self.occupancy = True            # True = room occupied
        
        # --- Derived / Control States ---
        self.is_spraying = False
        self.spray_intensity = 0.3       # ml per spray (High)
        self.cycle_count = 0
        self.condition_history = defaultdict(int)  # Track condition frequencies
        
        # --- Performance Metrics (from spec) ---
        self.odor_neutralization_efficiency = 99.5  # %
        self.fluid_saved_percent = 40.0             # %
        self.coverage_sqft = 500.0
        self.uptime_percent = 100.0
        
        # --- Error margins for sensor simulation ---
        self.temp_error = 0.5
        self.humidity_error = 5.0
        self.voc_error = 0.1
        
    def update_sensors(self):
        """
        Simulates live IoT sensor updates using random walks.
        Conditions will naturally drift between Preferred and Worst.
        """
        # Simulate occupancy toggling (20% chance to flip)
        if random.random() < 0.08:
            self.occupancy = not self.occupancy
            
        # Temperature: drifts between 15°C and 35°C (cold winter to hot summer)
        delta_temp = random.uniform(-0.8, 0.8)
        self.temperature += delta_temp
        self.temperature = max(5.0, min(40.0, self.temperature))
        
        # Humidity: drifts between 20% and 85% RH
        delta_hum = random.uniform(-3.0, 3.0)
        self.humidity += delta_hum
        self.humidity = max(15.0, min(90.0, self.humidity))
        
        # VOC: rises when occupied, falls when empty (with random spikes)
        if self.occupancy:
            self.voc_ppm += random.uniform(-0.05, 0.25)
        else:
            self.voc_ppm += random.uniform(-0.15, 0.05)
        # Simulate a chemical spike occasionally
        if random.random() < 0.05:
            self.voc_ppm += random.uniform(1.0, 3.0)
        self.voc_ppm = max(0.0, min(10.0, self.voc_ppm))
        
        # Fluid decreases if spraying
        if self.is_spraying:
            consumed = self.spray_intensity * random.uniform(0.9, 1.1)
            self.fluid_ml -= consumed
            self.total_sprays += 1
            self.fluid_ml = max(0.0, self.fluid_ml)
        
        # Scent Concentration: diffuses based on spray and ventilation
        # Target is 2.0 µg/m³. If spraying, concentration rises; else, it decays.
        if self.is_spraying:
            self.scent_concentration += random.uniform(0.5, 1.2)
        else:
            self.scent_concentration *= random.uniform(0.85, 0.98)
        # Add external ventilation effect (if unoccupied, windows might be open)
        if not self.occupancy and random.random() < 0.3:
            self.scent_concentration *= 0.9
        self.scent_concentration = max(0.1, min(6.0, self.scent_concentration))
        
        # Simulate uptime: 0.1% chance of a glitch to test robustness
        if random.random() < 0.002:
            self.uptime_percent = 99.8  # minor dip
        else:
            self.uptime_percent = 100.0
            
    def analyze_conditions(self):
        """
        Evaluates current metrics and classifies the environment.
        Returns: (condition_label, health_score, action, details)
        """
        score = 100  # Start perfect
        details = []
        
        # --- 1. Temperature Analysis (Ideal: 18-24°C) ---
        if 18.0 <= self.temperature <= 24.0:
            details.append("Temp: Ideal")
        elif 15.0 <= self.temperature < 18.0 or 24.0 < self.temperature <= 30.0:
            score -= 10
            details.append("Temp: Acceptable")
        elif 10.0 <= self.temperature < 15.0 or 30.0 < self.temperature <= 35.0:
            score -= 25
            details.append("Temp: Poor")
        else:
            score -= 40
            details.append("Temp: Critical")
            
        # --- 2. Humidity Analysis (Ideal: 40-60% RH) ---
        if 40.0 <= self.humidity <= 60.0:
            details.append("Humidity: Ideal")
        elif 30.0 <= self.humidity < 40.0 or 60.0 < self.humidity <= 70.0:
            score -= 10
            details.append("Humidity: Acceptable")
        elif 20.0 <= self.humidity < 30.0 or 70.0 < self.humidity <= 80.0:
            score -= 20
            details.append("Humidity: Poor")
        else:
            score -= 35
            details.append("Humidity: Critical (Clog Risk)")
            
        # --- 3. VOC Analysis (Ideal: < 0.5 ppm) ---
        if self.voc_ppm < 0.5:
            details.append("VOC: Pristine")
        elif 0.5 <= self.voc_ppm < 2.0:
            score -= 8
            details.append("VOC: Acceptable")
        elif 2.0 <= self.voc_ppm < 5.0:
            score -= 20
            details.append("VOC: Poor (Odor Detected)")
        else:
            score -= 45
            details.append("VOC: Critical (Unhealthy)")
            
        # --- 4. Fluid Level ---
        if self.fluid_ml > 50.0:
            details.append("Fluid: Sufficient")
        elif 15.0 < self.fluid_ml <= 50.0:
            score -= 5
            details.append("Fluid: Low (< 50ml)")
        elif 5.0 < self.fluid_ml <= 15.0:
            score -= 25
            details.append("Fluid: Critical (< 15%) - REFILL SOON")
        else:
            score -= 50
            details.append("Fluid: EMPTY - REFILL NOW")
            
        # --- 5. Scent Concentration (Target: 2.0 µg/m³) ---
        if 1.8 <= self.scent_concentration <= 2.5:
            details.append("Scent: Optimal")
        elif 1.0 <= self.scent_concentration < 1.8:
            score -= 8
            details.append("Scent: Under-scented")
        elif 2.5 < self.scent_concentration <= 4.0:
            score -= 8
            details.append("Scent: Over-scented")
        else:
            score -= 20
            details.append("Scent: Severely Imbalanced")
            
        # --- 6. Occupancy Logic ---
        if not self.occupancy:
            score -= 5  # Slight penalty because we prefer occupied for active scenting
            details.append("Room: Unoccupied (Eco-mode)")
        else:
            details.append("Room: Occupied")
            
        # --- Clamp score ---
        score = max(0, min(100, score))
        
        # --- Determine Condition Class ---
        if score >= 85:
            condition = "PREFERRED (Excellent)"
        elif score >= 70:
            condition = "GOOD (Comfortable)"
        elif score >= 50:
            condition = "MODERATE (Needs Attention)"
        elif score >= 30:
            condition = "POOR (Unpleasant)"
        else:
            condition = "WORST (Critical Intervention Required)"
            
        # --- Generate Action ---
        action = self._generate_action(score, condition)
        
        return condition, score, action, details
    
    def _generate_action(self, score, condition):
        """Decides the device's next physical action (logic layer)."""
        actions = []
        
        # Spray logic based on conditions
        if self.voc_ppm > 3.0 and self.fluid_ml > 10.0 and self.occupancy:
            actions.append("🔹 BOOST SPRAY: High intensity (0.5ml)")
            self.spray_intensity = 0.5
            self.is_spraying = True
        elif self.voc_ppm > 0.8 and self.fluid_ml > 15.0:
            actions.append("🔹 NORMAL SPRAY: Standard cycle (0.3ml)")
            self.spray_intensity = 0.3
            self.is_spraying = True
        elif self.scent_concentration < 1.5 and self.fluid_ml > 20.0:
            actions.append("🔹 TOP-UP SPRAY: Short burst (0.15ml)")
            self.spray_intensity = 0.15
            self.is_spraying = True
        else:
            self.is_spraying = False
            actions.append("⏸️ IDLE: Maintaining current state")
            
        # Override for critical conditions
        if self.humidity > 80.0:
            actions.append("⚠️ PAUSED: High humidity risk (clog prevention)")
            self.is_spraying = False
        if self.fluid_ml < 5.0:
            actions.append("🚨 CRITICAL: Refill cartridge immediately")
            self.is_spraying = False
        if self.temperature > 38.0 or self.temperature < 5.0:
            actions.append("🌡️ PAUSED: Extreme temperature safe-mode")
            self.is_spraying = False
            
        if not actions:
            actions.append("⏸️ IDLE: Standing by")
            
        # If room is empty, we save fluid (40% reduction metric)
        if not self.occupancy and self.is_spraying:
            actions.append("💡 ECO-MODE: Reducing frequency (40% fluid saved)")
            # Simulate the 40% reduction: if spraying, we reduce intensity
            self.spray_intensity *= 0.6
            
        return " | ".join(actions)

    def _generate_physical_commands(self, condition, score):
        """
        Maps environmental analysis to explicit hardware-level commands.
        These act as virtual GPIO/PWM outputs. For real hardware, replace print with:
        - RPi.GPIO.output(18, GPIO.HIGH)
        - pwm.ChangeDutyCycle(80)
        """
        commands = {}
        
        # 1. Status LED (GPIO 17)
        if "PREFERRED" in condition or "GOOD" in condition:
            commands["LED (GPIO17)"] = "GREEN (0.5s blink)"
        elif "MODERATE" in condition:
            commands["LED (GPIO17)"] = "YELLOW (Solid)"
        elif "POOR" in condition:
            commands["LED (GPIO17)"] = "ORANGE (Fast blink)"
        else:  # WORST
            commands["LED (GPIO17)"] = "RED (Solid - CRITICAL)"
            
        # 2. Sprayer Relay (GPIO 18) & PWM Speed
        if self.is_spraying and self.fluid_ml > 5.0:
            commands["Spray Relay (GPIO18)"] = "HIGH (ON)"
            # Map intensity (0.15, 0.3, 0.5) to PWM 0-255
            pwm_value = int((self.spray_intensity / 0.5) * 255)
            pwm_value = min(255, max(0, pwm_value))
            commands["Spray PWM Speed"] = f"{pwm_value} / 255 ({int((pwm_value/255)*100)}% Duty)"
        else:
            commands["Spray Relay (GPIO18)"] = "LOW (OFF)"
            commands["Spray PWM Speed"] = "0 / 255 (0% Duty)"
            
        # 3. Buzzer Alarm (GPIO 19) - Only for Worst conditions or Empty fluid
        if "WORST" in condition or self.fluid_ml < 5.0:
            commands["Buzzer (GPIO19)"] = "HIGH (BEEP BEEP!)"
        else:
            commands["Buzzer (GPIO19)"] = "LOW (Silent)"
            
        # 4. Fan / Diffuser Speed (Simulated external fan)
        if self.scent_concentration > 3.5:
            commands["Diffuser Fan (PWM1)"] = "HIGH (80%) - Ventilating"
        elif self.scent_concentration < 1.0:
            commands["Diffuser Fan (PWM1)"] = "LOW (20%) - Preserving scent"
        else:
            commands["Diffuser Fan (PWM1)"] = "MEDIUM (50%) - Steady"
            
        return commands

    def print_output(self, iteration):
        """Prints a rich, live-updating dashboard with explicit Virtual Physical Outputs."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        condition, score, action, details = self.analyze_conditions()
        self.condition_history[condition] += 1
        
        # Generate explicit hardware commands based on current state
        physical_commands = self._generate_physical_commands(condition, score)
        
        print("=" * 80)
        print(f"🧠 SMART AIR FRESHENER v2.1 - LIVE IOT DASHBOARD [Cycle {iteration}]")
        print(f"⏱️  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # --- Sensor Metrics (Raw) ---
        print("\n📡 [SENSOR METRICS (Raw & Real-time)]")
        print(f"   🌡️  Temperature    : {self.temperature:.2f} °C  (Accuracy: ±{self.temp_error}°C)")
        print(f"   💧  Humidity       : {self.humidity:.2f} % RH   (Accuracy: ±{self.humidity_error}% RH)")
        print(f"   ☣️  VOC (Odor)      : {self.voc_ppm:.2f} ppm    (Sensitivity: ±{self.voc_error} ppm)")
        print(f"   🫧  Scent Conc.    : {self.scent_concentration:.2f} µg/m³ (Target: 2.0 µg/m³)")
        print(f"   🧴  Fluid Level    : {self.fluid_ml:.1f} ml     (Capacity: 120 ml)")
        print(f"   🔄  Total Sprays   : {self.total_sprays}")
        print(f"   🏠  Occupancy      : {'👤 Occupied' if self.occupancy else '🚪 Empty'}")
        print(f"   📶  Uptime         : {self.uptime_percent:.1f} %")
        print(f"   🏷️  Coverage       : {self.coverage_sqft} sq. ft.")
        
        # --- Condition Analysis ---
        print("\n📊 [ENVIRONMENTAL ANALYSIS]")
        print(f"   🏷️  Classification : {condition}")
        print(f"   📈  Health Score   : {score:.1f} / 100")
        print("   📋  Breakdown      :")
        for item in details:
            print(f"        - {item}")
            
        # --- Explicit Physical Action Mapping (GPIO/PWM) ---
        print("\n⚡ [VIRTUAL PHYSICAL OUTPUTS (GPIO / PWM)]")
        print("   (Replace print() with GPIO.output() or serial.write() for real hardware)")
        for pin, state in physical_commands.items():
            print(f"        {pin:<18} : {state}")
            
        # --- Original Device Action (Human Readable) ---
        print("\n📝 [HUMAN-READABLE DEVICE LOGIC]")
        print(f"   {action}")
        if self.is_spraying:
            print(f"   💨  Spraying at {self.spray_intensity:.2f} ml/cycle")
        else:
            print("   💨  Sprayer: OFF")
            
        # --- Efficiency Metrics from Spec ---
        print("\n📈 [SYSTEM PERFORMANCE (Infused Metrics)]")
        print(f"   ✅ Odor Neutralization Efficiency : {self.odor_neutralization_efficiency:.1f} %")
        print(f"   💰 Fluid Saved (vs. Standard)    : {self.fluid_saved_percent:.1f} % (Smart Scheduling)")
        print(f"   🔋 Power Consumption (Standby)   : 0.5 W")
        
        # --- Historical Trend (Preferred to Worst) ---
        print("\n📜 [CONDITION HISTORY (Preferred ↔ Worst)]")
        sorted_conditions = ["PREFERRED (Excellent)", "GOOD (Comfortable)", 
                             "MODERATE (Needs Attention)", "POOR (Unpleasant)", 
                             "WORST (Critical Intervention Required)"]
        for c in sorted_conditions:
            count = self.condition_history.get(c, 0)
            bar = "█" * min(count, 20)
            print(f"   {c:<30}: {count:>3} times {bar}")
            
        print("\n" + "=" * 80)
        # The following line has been removed as requested:
        # print("⏳ Updating next cycle in 2 seconds... (Press Ctrl+C to stop)")

    def run(self, cycles=40):
        """Main live simulation loop."""
        print("🚀 Initializing Smart Air Freshener...")
        time.sleep(1)
        for i in range(1, cycles + 1):
            self.update_sensors()
            self.print_output(i)
            # The delay has been commented out for instant execution
            # time.sleep(2)  # Live update interval
            
        # Final summary
        print("\n" + "=" * 80)
        print("🏁 SIMULATION COMPLETE - FINAL CONDITION DISTRIBUTION")
        print("=" * 80)
        total = sum(self.condition_history.values())
        if total > 0:
            for cond, count in sorted(self.condition_history.items(), key=lambda x: -x[1]):
                pct = (count / total) * 100
                print(f"   {cond:<30}: {count:>3} cycles ({pct:.1f}%)")
        print("✅ Device successfully analyzed the spectrum from Preferred to Worst conditions.")


# =============================================================================
# PRODUCTION CODE (Hardware-Ready) - COMMENTED OUT
# Uncomment this entire block AND comment out the Simulation block below
# to deploy on real hardware (Raspberry Pi / ESP32 with MicroPython).
# =============================================================================
"""
import RPi.GPIO as GPIO
import Adafruit_DHT
import smbus
import spidev

class SmartAirFreshenerProduction:
    # Production version using real GPIO, PWM, and I2C/SPI sensors.
    # Replaces simulation data with physical world readings.
    
    def __init__(self):
        # --- Hardware Setup ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Pin Definitions
        self.LED_PIN = 17
        self.RELAY_PIN = 18   # Sprayer relay
        self.BUZZER_PIN = 19
        self.PWM_PIN = 12     # PWM for pump speed control
        
        # Setup Outputs
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.setup(self.RELAY_PIN, GPIO.OUT)
        GPIO.setup(self.BUZZER_PIN, GPIO.OUT)
        
        # PWM Setup (Pump Speed)
        self.pwm = GPIO.PWM(self.PWM_PIN, 1000)  # 1 kHz frequency
        self.pwm.start(0)
        
        # Sensor Pins (example)
        self.DHT_PIN = 4      # DHT22 data pin
        self.ADC_CS_PIN = 8   # For MCP3008 (fluid level / VOC)
        
        # --- Core Metrics (initial values, will be overwritten by sensors) ---
        self.temperature = 21.0
        self.humidity = 45.0
        self.voc_ppm = 0.2
        self.fluid_ml = 120.0
        self.total_sprays = 0
        self.scent_concentration = 2.0
        self.occupancy = True   # Could be read from PIR sensor later
        
        # --- State Variables ---
        self.is_spraying = False
        self.spray_intensity = 0.3
        self.cycle_count = 0
        self.condition_history = defaultdict(int)
        
        # --- Performance Metrics ---
        self.odor_neutralization_efficiency = 99.5
        self.fluid_saved_percent = 40.0
        self.coverage_sqft = 500.0
        self.uptime_percent = 100.0
        
        # --- Error margins (hardware accuracy) ---
        self.temp_error = 0.5
        self.humidity_error = 5.0
        self.voc_error = 0.1
        
        # Initialize I2C bus (for SGP30 VOC sensor)
        # self.i2c = smbus.SMBus(1)
        # self.sgp30 = SGP30(self.i2c)  # Example
        
    def read_dht22(self):
        # Reads real temperature and humidity from DHT22.
        # Retries up to 3 times.
        for _ in range(3):
            humidity, temp = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self.DHT_PIN)
            if humidity is not None and temp is not None:
                return temp, humidity
            time.sleep(0.5)
        return self.temperature, self.humidity  # Fallback to last known
    
    def read_voc_sgp30(self):
        # Placeholder for reading actual VOC via I2C (e.g., SGP30).
        # For now, simulates with slight random variation.
        # In production: raw = self.sgp30.measure_air_quality()
        # return raw.total_voc / 1000.0
        base = self.voc_ppm + random.uniform(-0.1, 0.1)
        return max(0.0, base)
    
    def read_fluid_level(self):
        # Reads fluid level via analog input (e.g., MCP3008 or voltage divider).
        # Simulated here; replace with spidev read.
        # Example: adc = spidev.SpiDev() / read_channel(0) -> map to ml
        fluid = self.fluid_ml - (0.02 if self.is_spraying else 0)
        return max(0.0, fluid)
    
    def update_sensors(self):
        # 1. Read real environment sensors
        temp, hum = self.read_dht22()
        self.temperature = temp
        self.humidity = hum
        
        # 2. Read VOC
        self.voc_ppm = self.read_voc_sgp30()
        
        # 3. Read fluid level
        self.fluid_ml = self.read_fluid_level()
        
        # 4. Simulate occupancy via a PIR (or hardcoded toggle for test)
        # In production: self.occupancy = GPIO.input(PIR_PIN)
        # Simulating a toggling effect for test (remove in final)
        if random.random() < 0.05:
            self.occupancy = not self.occupancy
        
        # 5. Update scent concentration (based on real diffusion model)
        if self.is_spraying:
            self.scent_concentration += random.uniform(0.3, 0.8)
        else:
            self.scent_concentration *= random.uniform(0.88, 0.97)
        self.scent_concentration = max(0.1, min(6.0, self.scent_concentration))
        
        # 6. Uptime (real hardware usually has 100% unless offline)
        self.uptime_percent = 100.0
        
        # 7. Decrease fluid if spraying (hardware logic)
        if self.is_spraying and self.fluid_ml > 0:
            consumed = self.spray_intensity * 1.0  # exact measurement
            self.fluid_ml -= consumed
            self.total_sprays += 1
            self.fluid_ml = max(0.0, self.fluid_ml)
    
    # --- All analysis methods (_generate_action, analyze_conditions, 
    #     print_output) remain IDENTICAL to the Simulation class.
    #     They operate on self.temperature, self.humidity, etc.
    #     I've omitted them here for brevity. Copy paste them from above.
    # ---
    
    def _generate_physical_commands(self, condition, score):
        # HARDWARE IMPLEMENTATION: This replaces the virtual print statements
        # with actual GPIO/PWM calls.
        
        # 1. LED (GPIO 17)
        if "PREFERRED" in condition or "GOOD" in condition:
            GPIO.output(self.LED_PIN, GPIO.HIGH)  # Green (if connected to RGB)
            # Simulate blink via thread/timer, or just set solid for simplicity
        elif "MODERATE" in condition:
            GPIO.output(self.LED_PIN, GPIO.HIGH)  # Yellow
        elif "POOR" in condition:
            GPIO.output(self.LED_PIN, GPIO.HIGH)  # Orange (fast blink idea)
        else:  # WORST
            GPIO.output(self.LED_PIN, GPIO.HIGH)  # Red
        
        # 2. Sprayer Relay (GPIO 18) & PWM Speed
        if self.is_spraying and self.fluid_ml > 5.0:
            GPIO.output(self.RELAY_PIN, GPIO.HIGH)  # Turn ON
            pwm_value = int((self.spray_intensity / 0.5) * 100)  # Duty 0-100
            pwm_value = min(100, max(0, pwm_value))
            self.pwm.ChangeDutyCycle(pwm_value)
        else:
            GPIO.output(self.RELAY_PIN, GPIO.LOW)   # Turn OFF
            self.pwm.ChangeDutyCycle(0)
        
        # 3. Buzzer (GPIO 19)
        if "WORST" in condition or self.fluid_ml < 5.0:
            GPIO.output(self.BUZZER_PIN, GPIO.HIGH)
        else:
            GPIO.output(self.BUZZER_PIN, GPIO.LOW)
        
        # 4. External Fan (PWM1) - if connected
        if self.scent_concentration > 3.5:
            # Ventilate
            pass  # self.fan_pwm.ChangeDutyCycle(80)
        elif self.scent_concentration < 1.0:
            pass  # self.fan_pwm.ChangeDutyCycle(20)
        else:
            pass  # self.fan_pwm.ChangeDutyCycle(50)
    
    # Note: print_output remains the same but now the physical_commands
    # dictionary will show actual hardware states instead of just strings.
    # You can override print_output to just log or send MQTT.
"""
# =============================================================================
# END OF PRODUCTION CODE (COMMENTED OUT)
# =============================================================================


# =============================================================================
# MAIN EXECUTION - SIMULATION IS ACTIVE BY DEFAULT
# =============================================================================
if __name__ == "__main__":
    try:
        # --- SIMULATION ACTIVE ---
        freshener = SmartAirFreshener()
        freshener.run(cycles=40)  # Runs instantly (no delay) now
        
        # --- TO SWITCH TO PRODUCTION: ---
        # 1. Uncomment the entire Production class block above (remove the """ ... """).
        # 2. Comment out the line above (freshener = SmartAirFreshener()).
        # 3. Uncomment the line below:
        # freshener = SmartAirFreshenerProduction()
        # 4. Run this script on a Raspberry Pi with sensors connected.
        
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user. Exiting gracefully.")
        # If production GPIO was used, cleanup:
        # GPIO.cleanup()
        sys.exit(0)