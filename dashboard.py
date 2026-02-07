# dashboard.py
import streamlit as st
from motor_library import load_motor
from thrust import calculate_thrust

st.title("🚀 Tau Rocket Motor Designer")

# Sliders for inputs
dt = st.sidebar.slider("Throat Diameter (mm)", 8.0, 15.0, 10.0)
length = st.sidebar.slider("Grain Length (mm)", 50.0, 150.0, 100.0)

# Run Sim instantly
# 1. Load a valid template motor first (instead of "custom")
# 'motor_quark3_04' or 'motor_12' are good base templates
motor = load_motor("motor_1")

# 2. Rename it so the report looks correct
motor.name = "Custom Design"

# 3. NOW apply your slider values to overwrite the template defaults
motor.Dt = dt
motor.L = length

F, Pc, t, _, _ = calculate_thrust(10000, motor, 0.95, 6.278)

# Plot
st.line_chart(Pc)