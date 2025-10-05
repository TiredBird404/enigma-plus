[中文简介](https://github.com/TiredBird404/enigma-plus/blob/main/README.sch.md)
# Introduction
**Enigma+**, is an encryption algorithm based on the Enigma machine used by Nazi Germany during World War II.
This algorithm reproduces the character conversion and encryption methods of the Enigma machine,
while introducing derivations in ***rotor generation***, ***unlimited parameter settings***, and ***expanded character support***.

***Note: This program is a personal experimental project , cannot be compared to modern encryption algorithms.***

## Run the Program
*This program imports tkinter, customtkinter, and hashlib libraries and uses Python 3.13.7 as its development environment.  
Ensure Python version 3.8 or higher is installed on your computer along with the customtkinter library to run this program:*
```bash
python3 -m pip install customtkinter
```

## Algorithm Logic
Enigma+'s computational logic is based on the Enigma machine, with following basically functioning logic:
- ***LOOP:*** Sequentially get the nth character in the text and perform encryption.
  - ***IF*** Character n is not in the character set: encrypt the next character.
  - ***GENERATE*** The rotor sequence and mechanical exchange value for character n.
  - ***EXCHANGE*** Character n with the character corresponding to it in the user exchange configuration.
  - ***LOOP:*** Positive order: Transforms character n into rotor r through the rotor sequence, cycling until all rotors have been processed.
    - ***GET*** the position of character n in the character library, add it to the offset value of the current rotor, and finally obtain the offset character.
    - ***FIND*** the character position L corresponding to the offset character within the rotor, and finally locate the character corresponding to position L in the character library.
  - ***EXCHANGE*** Character n with the character corresponding to it in the mechanical exchange configuration.
  - ***LOOP:*** Reverse order: Transforms character n into rotor r through the rotor sequence, cycling until all rotors have been processed.
    - ***FIND*** the character position L corresponding to character n in the character library, and find the character c corresponding to position L in the rotor r.
    - ***GET*** the location of character c in the character library, reduce it by the offset value of the current rotor, and finally obtain the offset character n.
  - ***EXCHANGE*** Character n with the character corresponding to it in the user exchange configuration.
  - ***ROTATION:*** Turn the initial offset value by the strength of rotation, then perform following carry operations.
- ***RETURN*** the concatenation of characters processed in the loop.

These algorithms ran the logic of the original Enigma machine, and added separate rotors for each character, making it more complex. It also retained Enigma's algorithm of encryption and decryption working in parallel.

## Character Library Support Extension
The program does not define character libraries using pre-set values , instead invoking them through calculations and loops.
Consequently, character libraries can theoretically be modified or expanded within the source code to meet user requirements.
The only consideration is that, due to character conversion rules, the length of the character library must not be odd.
If incorrectly configured, the program will display error messages at startup.

## Generation of Rotors
For each character in the text, a complete set of rotors is generated. Each rotor is a string produced by shuffling the character library.
The shuffling of the character library is based on the ***Fisher-Yates shuffle algorithm***,
and the permutation random values used in the shuffle algorithm are integer-converted **hash values** *(based on the SHA3-512 algorithm)*.
Each hash value is computed based on processed user parameters, meaning user input significantly affects the final result.
Even minor deviations can lead to vastly different outputs. The logic for generating a single rotor is outlined below:
- ***SET*** Initial Value = Character Conversion Parameter Integration + Convert to String(Sum of Initial Offsets * Number of Rotor Sets + Current Offset Value + Rotation Intensity + Sequence of Currently Generated Rotors) -> String
- ***REPETITION*** generation to provide hash values for all characters in the character set, repeat in positive order.
  - ***SET*** ComputingValue = InitialValue + String(InitialValueLength * (InitialValueLength - CurrentSequenceCount)) -> String.
  - ***CALCULATE*** the hash value from the input value, and convert the hash value to an entire number.
- ***GET*** all values computed in the loop and feed them into the pseudorandom array.
- ***SHUFFLE:*** Using the Fisher-Yates shuffle algorithm, the character library gets scrambled based on the generated pseudorandom number array.
- ***RETURN*** Shuffle Results

## Unlimited of Parameters
In the original Enigma machine, only 3 to 4 existing rotors could be used. 
These were placed into the machine in an optional sequence, and finally, an initial offset was set for these 3 to 4 rotors. 
The value of the initial offset was also limited to 1 to 26 (the length of the character library), and the final rotation step was only 1 step. 
In this program, however, the number of rotors, offset values, and rotation strength are theoretically unlimited. 
These values are all closely related to the final output and significantly increase the difficulty of brute-force attacks. 
Additionally, to allow offset values to carry over without being constrained by modulo operations, a dedicated carry algorithm was written into the code. 
The logic is as follows:
- ***COPY*** the offset values from one array to another.
- ***MODULO:*** Calculate the remainder of each value in the copied array for subsequent carry calculations.
- ***ROTATION:*** Rotate the offset array and the copied array's first value depending on the rotation strength.
- ***REPEAT:*** Perform carry, forward repetition (offset array size - 1) times, loop count expressed as n:
  - ***ADD*** the integer part of the nth value in the copied array divided by the character library length (removing the decimal point, serving as the carry digit) to the n+1st value in the copied array and offset array.
- ***RETURN*** the offset array after carry propagation.
