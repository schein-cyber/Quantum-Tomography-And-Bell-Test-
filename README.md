# Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light-
This repository stores all of the code used for the "Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light" experiment article, in which quantum phenomena are classically emulated using a pulsed laser, measuring quantum tomography and implementing bell's test experimently. We began by emulating a quantum tomography system by sending pulses from a classical laser, with randomized polarization, which goes into a system of optical devices, starting from a beam splitter, 

# Code 1 - Quantum Tomography And Bell Test/Quantum Tomography - Raw Data Extraction.py
Description - This code takes the tomography videos as inputs, provides a graph of the total intensity for each frame of the first video from which the user may select 5 frames with maximal intensity. From these 5 frames, the user may then choose 4 rectangles where the intensities of each of the measured pulses (Alice H/V and Bob H/V) are to be measured. It then goes over the three tomography video files (10, 25, 50 bits) and produces intensity graphs for each of the pulses throughout time, which are then stored into npz files.

Inputs - 

outputs - 

# Code 2 - Quantum Tomography Thresholds.py
Description - This code is to be used after code 1 has been implemented. It takes the unfiltered pulse intensity graphs and allows the user to manually choose the thresholds for each graph by clicking on the intensity graph at some intensity height. This is done in order to filter noise. 

inputs - 

outputs - 

# Code 3 - 





