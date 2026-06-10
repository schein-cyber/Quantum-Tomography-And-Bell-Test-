# Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light
This repository stores all of the code used for the "Divide And Conquer: Emulating Quantum Tomography and Bell Tests with Classical Light" experiment article, in which quantum phenomena are classically emulated using a pulsed laser, measuring quantum tomography and implementing bell's test experimently. We began by emulating a quantum tomography system by sending pulses from a classical laser, with randomized polarization, which goes into a system of optical devices, starting from a beam splitter, and then going through another polarizing beam splitter, ending up in 4 detectors, labeled Alice H/V and Bob H/V, there is also an option to turn on a HWP before the first beam splitter, which essentially switches Bob's H and V. These measurements were recorded into 3 video files, for 10, 25 and 50 pulses respectively, these videos are then analyzed by this code, to produce density matrices for the 3 cases with and without the HWP, resulting in a total of 6 density matrices. In order to validate our theoretical and numerical methods used in this experiment, we additionally performed a simulation of the same exact system, for the a 50, 100 and 1000 bits, with and without the HWP, the code used for this simulation and the presentation of its density matrices in a similar manner to that of the experiment itself is presented in this repository.

In the second part of the experiment we showed that the system breaks the Bell inequality, and is then essentially quantum. We used a similar random polarization pulsed laser, with the same optical devices, only now there are only two detectors labeled Alice and Bob, and instead of the polarized beam splitter there is a polarizier, set in 16 different angle compositions, consisting of all possible combinations of (a,b) for a in [0,90,45,-45] and b in [22.5,-22.5,67.5,112.5]. For each of these combinations a measurement video was produced, resulting in 16 measurement videos. These videos are then analyzed by this code to produce the Bell parameter S, which is bigger then 2 and hence indicates that the system is essentially quantum. 

## Code 1 - Random Polarization.py
### Description 
This code provides the random polarizations of the laser, through a random series of 0s and 1s.

### Inputs 
This code takes the number of pulses as an input.

### Outputs 
This code produces a random series of 0s and 1s at the length of the number of pulses.

## Code 2 - Quantum Tomography - Simulation.py

### Description 
This code contains the simulation of the quantum tomography experiment. The system is completely mimiced by the code, including the optical setup and the random polarization of the laser. The code emulates 3 total bit amounts, 50, 100 and 1000. It then constructs the density matrices of the corresponding measurements, and plots them on a 3d graph similarly the density matrices codes. Additionally, the code mimics the HWP by switching Bob's H and V states, plotting the corresponding density matrices as well.

### inputs 
There are no inputs needed in order to run this code. The number of bits may be changed manually if one desires to do so.

### outputs 
6 Density matrices in numerical form, for the following cases: 50, 100 and 1000 bits, with or without a HWP. 6 Graphs of the 6 density matrices in a 3d representation, with the corresponding labels. 


## Code 3 - Quantum Tomography - Raw Data Extraction.py
### Description 
This code is used to extract the raw pulse intensity data of the tomography measurement videos. It takes the tomography videos as inputs, provides a graph of the total intensity for each frame of the first video from which the user may select 5 frames with maximal intensity. From these 5 frames, the user may then choose 4 rectangles where the intensities of each of the measured pulses (Alice H/V and Bob H/V) are to be measured. It then goes over the three tomography video files (10, 25, 50 bits) and produces intensity graphs for each of the pulses throughout time, which are then stored into npz files.

### Inputs 
"BASE DIR" - allows the user to set the filename to match their computer, for example: r"C:\Users\User\Downloads". 3  measurement video mp.4 files, named  "Tomography i bits.mp4" for i in [10, 25, 50]. The user may change this by changing the files in "VIDEO_FILES"
Note: These measurement videos are not attached to this repository, as they are too large. 

### outputs 
3 raw intensity npz files, named "results_tomography__bits.npz" for i in [10, 25, 50]. 

## Code 4 - Quantum Tomography - Thresholds.py
Description - This code is to be used after code 3 has been implemented. It takes the unfiltered pulse intensity graphs and allows the user to manually choose an intensity threshold for each graph by clicking on the intensity graph at some intensity height. This is done in order to filter noise. 

### inputs 
The 3 raw intesity npz files produced from the previous code, named "results_tomography_ן_bits.npz" for i in [10, 25, 50].

### outputs 
3 thresholded intensity npz files, named "thresholded_results_tomography__bits.npz" for i in [10, 25, 50]. 

## Code 5 - Quantum Tomography - Density Matrices.py
### Description 
This code is to be used after code 4 has been implemented. It takes the thersholded quantum tomography files, binarizes the intensities into 0s or 1s, accounts for the same pulse being measured in a few consequenting frame. It then uses the binarized intensities in order to construct the effective quantum state of the system, from which a density matrix is produced by taking a ket bra multiplication of this state with itself. The density matrices are calculated and plotted for each of the 3 videos (10, 25, 50 bits). The plots are on a 3d graph, as usually used in tomography. In addition, this code mimics the HWP by switching Bob's H and V states, to reproduce density matrices with a HWP. These matrices are then additinally plotted, resulting in a total of 6 density matrices, and 6 plots of the density matrices plotted in 3d.

### inputs 
The 3 thresholded intensity npz files  produced from the previous code, named "thresholded_results_tomography_ן_bits.npz" for i in [10, 25, 50]. 

### outputs 
6 Density matrices in numerical form, labeled for the corresponding amount of bits [10,25,50] and with or with a HWP. 6 plots of the density matrices plotted in 3d, with the corresponding titles.

## Code 6 - Bell Test - Raw Data Extraction.py
### Description 
This code is used to extract the raw pulse intensity data of the bell test measurement videos. The code loads each video separetely, loads the highest intensity frame for this video, and then allows the user to choose the two rectangles for the intensity measurements by clicking on two points on the frame. The code allows the user to label these ROIs (Alice and Bob in our analysis). The code then processes the video using these ROIs and produces intensity over time graphs for both Alice and Bob, which are stored as npz files.

### inputs 
16 mp.4 Video files named ""Bell a, b.mp4"" for a in [0,90,45,-45] and b in [22.5,-22.5,67.5,112.5]. The user should change "BASE_DIR" and "PROJECT_DIR" to match their own computer

### outputs 
16 Raw intesity npz files, named "results_Bell_a__b.npz" for a in [0,90,45,-45] and b in [22.5,-22.5,67.5,112.5].

## Code 7 - Bell Test - S Calculation.py
### Description 
This code is to be used after code 6 has been implemented. It takes the raw intensity data files of the bell test measurements, allows the user to choose a uniform threshold across all 16 videos for Alice and Bob separetly. It then measurse the overlap between Alice's and Bob's measurements for each video, and counts these overlaps to calculate the Bell parameter S defined in our article. It then gives this S value as an output. To estimate the error, each coincidence count is treated as a binomial variable, since each pulse has a probability of being a coincidence, and is independent of the others. n = N_pulses, and we estimated p = N(a,b)/N_pulses, and then used the standard deviation of a binomial variable as the error for the coincidence count. From the error in each count, the code estimates the error dS and outputs it as well. 

### inputs 
The 16 raw intesity npz files produced from the previous code, named "results_Bell_a__b.npz" for a in [0,90,45,-45] and b in [22.5,-22.5,67.5,112.5].


### outputs 
Table of 16 N(a,b) values for all angle combinations ofa in [0,90,45,-45] and b in [22.5,-22.5,67.5,112.5]. The value of the Bell parameter S with an error dS.




