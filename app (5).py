import subprocess
import sys

# Force install necessary packages if not found
required_packages = ["numpy", "matplotlib", "gradio"]
for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import numpy as np
import matplotlib.pyplot as plt
import gradio as gr

# Question 1
def calculate_dissolved_oxygen(initial_DO, OTE, consumption_rate, time_steps):
    DO = np.zeros(time_steps)
    DO[0] = initial_DO
    
    for t in range(1, time_steps):
        OTR = OTE * (DO[t-1])  # Simplified OTR model
        DO[t] = DO[t-1] + OTR - consumption_rate
    
    return DO

def ot_app(initial_DO, OTE, consumption_rate, time_steps):
    DO_profile = calculate_dissolved_oxygen(initial_DO, OTE, consumption_rate, time_steps)
    
    plt.figure(figsize=(10, 5))
    plt.plot(DO_profile)
    plt.title('Dissolved Oxygen Profile Over Time')
    plt.xlabel('Time Steps')
    plt.ylabel('Dissolved Oxygen (mg/L)')
    plt.grid()
    plt.close()  # Prevents Gradio from displaying the plot automatically
    return plt

# Question 2
def calculate_distribution_ratio(C_a, K):
    return K * C_a / (1 + K * C_a)

def llx_app(K):
    C_a = np.linspace(0, 1, 100)
    D = calculate_distribution_ratio(C_a, K)
    
    plt.figure(figsize=(10, 5))
    plt.plot(C_a, D, label='Distribution Curve')
    plt.title('Distribution Curve for Liquid-Liquid Extraction')
    plt.xlabel('Concentration in Phase A (C_a)')
    plt.ylabel('Distribution Ratio (D)')
    plt.grid()
    plt.legend()
    plt.close()
    return plt

# Question 3
def mccabe_thiele(feed_comp, xD, xB, R):
    x = np.linspace(0, 1, 100)
    y = R/(R+1) * x + xD/(R+1)
    
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, label='Equilibrium Curve')
    plt.plot(x, x, 'r--', label='45 Degree Line')
    plt.title('McCabe-Thiele Diagram')
    plt.xlabel('Liquid Composition (x)')
    plt.ylabel('Vapor Composition (y)')
    plt.grid()
    plt.legend()
    plt.close()
    return plt

# Question 4
def reactor_volumes(feed_rate, k, target_conversion):
    V_CSTR = feed_rate * (1 - target_conversion) / (k * target_conversion)
    V_PFR = feed_rate / k * (1 / target_conversion - 1)
    
    return V_CSTR, V_PFR

def reactor_app(feed_rate, k, target_conversion):
    V_CSTR, V_PFR = reactor_volumes(feed_rate, k, target_conversion)

    # Plotting for PFR
    length = np.linspace(0, 1, 100)
    conversion_profile = 1 - np.exp(-k * feed_rate * length)

    plt.figure(figsize=(10, 5))
    plt.plot(length, conversion_profile)
    plt.title('Conversion Profile for PFR')
    plt.xlabel('Reactor Length')
    plt.ylabel('Conversion')
    plt.grid()
    plt.close()

    return V_CSTR, V_PFR, plt

# Create individual interfaces
ot_interface = gr.Interface(fn=ot_app, 
                             inputs=["number", "number", "number", "number"],
                             outputs="plot",
                             title="Oxygen Transfer Rate Calculator",
                             description="Simulate the dissolved oxygen (DO) profile in an aeration tank.")

llx_interface = gr.Interface(fn=llx_app, 
                              inputs="number",
                              outputs="plot",
                              title="Liquid-Liquid Extraction Calculator",
                              description="Calculate the distribution ratio of a solute between two immiscible solvents.")

distillation_interface = gr.Interface(fn=mccabe_thiele, 
                                       inputs=["number", "number", "number", "number"],
                                       outputs="plot",
                                       title="Distillation Column Calculator",
                                       description="Calculate the number of theoretical stages required for separating a binary mixture.")

reactor_interface = gr.Interface(fn=reactor_app, 
                                  inputs=["number", "number", "number"],
                                  outputs=["number", "number", "plot"],
                                  title="Reactor Design Calculator",
                                  description="Calculate the reactor volume for CSTR and PFR for a first-order reaction.")

# Combine all interfaces into a tabbed interface
tabbed_interface = gr.TabbedInterface(
    [ot_interface, llx_interface, distillation_interface, reactor_interface],
    tab_names=["Oxygen Transfer Rate", "Liquid-Liquid Extraction", "Distillation", "Reactor Design"]
)

# Launch the tabbed interface
if __name__ == "__main__":
    tabbed_interface.launch()
