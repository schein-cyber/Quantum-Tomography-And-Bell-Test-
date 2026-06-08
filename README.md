# Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light-
This repository stores all of the code used for the "Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light" experiment article, in which quantum phenomena are classically emulated using a pulsed laser, measuring quantum tomography and implementing bell's test experimently. We began by emulating a quantum tomography system by sending pulses from a classical laser, with randomized polarization, which goes into a system of optical devices, starting from a beam splitter, 

# Code 1 - Random Polarization.py
Description - This code provides the random polarizations of the laser, through a random series of 0s and 1s.

Inputs - This code takes the number of pulses as an input.

Outputs - This code produces a random series of 0s and 1s at the length of the number of pulses.

# Code 2 - Quantum Tomography - Simulation.py

Description - This code contains the simulation of the quantum tomography experiment. The system is completely mimiced by the code, including the optical setup and the random polarization of the laser. The code emulates 3 total bit amounts, 1000, 5000, 10000 and then constructs the density matrices of the corresponding measurements, and plots them on a 3d graph similarly the density matrices codes. Additionally, the code mimics the HWP by switching Bob's H and V states, plotting the corresponding density matrices as well.

inputs - 

outputs -


# Code 3 - Quantum Tomography - Raw Data Extraction.py
Description - This code is used to extract the raw pulse intensity data of the tomography measurement videos. It takes the tomography videos as inputs, provides a graph of the total intensity for each frame of the first video from which the user may select 5 frames with maximal intensity. From these 5 frames, the user may then choose 4 rectangles where the intensities of each of the measured pulses (Alice H/V and Bob H/V) are to be measured. It then goes over the three tomography video files (10, 25, 50 bits) and produces intensity graphs for each of the pulses throughout time, which are then stored into npz files.

Inputs - 

outputs - 

# Code 4 - Quantum Tomography - Thresholds.py
Description - This code is to be used after code 3 has been implemented. It takes the unfiltered pulse intensity graphs and allows the user to manually choose an intensity threshold for each graph by clicking on the intensity graph at some intensity height. This is done in order to filter noise. 

inputs - 

outputs - 

# Code 5 - Quantum Tomography - Density Matrices.py
Description - This code is to be used after code 4 has been implemented. It takes the thersholded quantum tomography files, binarizes the intensities into 0s or 1s, accounts for the same pulse being measured in a few consequenting frame. It then uses the binarized intensities in order to construct the effective quantum state of the system, from which a density matrix is produced by taking a ket bra multiplication of this state with itself. The density matrices are calculated and plotted for each of the 3 videos (10, 25, 50 bits). The plots are on a 3d graph, as usually used in tomography. In addition, this code mimics the HWP by switching Bob's H and V states, to reproduce density matrices with a HWP. These matrices are then additinally plotted, resulting in a total of 6 density matrices, and 1 plot with the 6 density matrices plotted in 3d.

inputs - 

outputs -

# Code 6 - Bell Test - Raw Data Extraction.py
Description -  This code is used to extract the raw pulse intensity data of the bell test measurement videos.

inputs - 

outputs -

# Code 7 



