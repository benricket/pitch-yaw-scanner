"""
Python script to read analog sensor data from serial connection,
convert readings to distances, and plot distances in cartesian
coordinates in a 3d scatter plot.
"""

import sys
import matplotlib.pyplot as plt
import numpy as np
from serial import Serial, SerialException

# Define constants dependent on circuit and calibration curve for sensor
# Constants found by calibration and validation
VOLTAGE_IN = 5
NUM_ANALOG_READINGS = 1024
INVERSE_CM_PER_READING = 0.00008979394408
INVERSE_CM_AT_ZERO = -0.00269829391

PRINT_DEBUG = False


def main():
    """
    Main function to gather, process, and plot data
    """

    cxn = init_connection()
    pitch_list = []
    yaw_list = []
    reading_list = []
    is_waiting = True  # Wait for user input before starting scan

    while True:
        print("start loop")
        if is_waiting:
            # Prompt user to begin scanning
            user_in = input("Run script to gather + plot data? y/n\n")
            if user_in.strip().lower() in {"y", "yes"}:
                while user_in not in {1, 2, 3, 4, 5}:
                    user_in = int(
                        input(
                            "Enter mode: 1 (Yaw servo only), 2 (Pitch servo only), 3 (Both servos), 4 (Single data point), 5 (Load data from recorded_scan.csv): "
                        )
                    )
                if user_in == 5:
                    # If we want to use our previous data, don't both scanning again
                    # We just load the data, plot it, and exit
                    data = np.loadtxt("recorded_scan.csv", delimiter=",")
                    display_data(data)
                    sys.exit()
                else:
                    is_waiting = False
                    # Arduino script expects ascii encoded data
                    ascii_line = f"{user_in+1}\n".encode("ascii")
                    cxn.write(ascii_line)  # Begins the servo movement
                    cxn.flush()

        else:
            result = cxn.readline().decode("ascii").strip()

            if len(result) < 1:  # Ignore incomplete data
                continue

            result_split = result.split(",")

            # Ignore incomplete data
            if len(result_split) < 3 or "" in result_split:
                continue

            # Useful information in case data processing is wrong
            if PRINT_DEBUG:
                print(type(result))
                print(result)
                print(result_split)
                print(type(result_split[0]))

            # Arduino script indicates scan is complete by passing
            # negatives; break out of loop upon receiving these
            if "-1" in result_split:
                break

            # Append readings to lists
            # Preallocating would be slightly faster but isn't
            # strictly necessary
            pitch_list.append((float(result_split[0]) - 90) * np.pi / 180)
            yaw_list.append(float(result_split[1]) * np.pi / 180)
            reading_list.append(int(result_split[2]))
            print(f"Decoded: {result}, reading: {result_split[2]}")

    cxn.write([int(0)])  # Pauses the servo controls

    processed, _ = process_data(pitch_list, yaw_list, reading_list)
    display_data(processed)  # Display the graphed scan data


def reading_to_dist(pitch_list, yaw_list, readings):
    """
    Use the provided transfer function of the sensor to convert readings
    into distances.

    Transfer function is calculated by fitting a line to the inverse of distance
    from a number of calibration points.

    Filters all input lists by removing points corresponding to distance sensor
    readings outside the calibration range, which aren't useful for us.

    Args:
        pitch_list (list[float]): pitch servo values, in rad
        yaw_list (list[float]): yaw servo values, in rad
        readings (list[int]): sensor readings

    Returns:
        pitches (list[float]): filtered pitch values
        yaws (list[float]): filtered yaw values
        dist_list (list[float]): linear distance to point, in cm
    """
    dist_list = []
    pitches = []
    yaws = []
    for index, reading in enumerate(readings):
        # Ignore values in the range we don't care about
        if reading < 420 and reading > 150:
            dist_list.append(
                1 / (INVERSE_CM_PER_READING * reading + INVERSE_CM_AT_ZERO)
            )
            pitches.append(pitch_list[index])
            yaws.append(yaw_list[index])
    return pitches, yaws, dist_list


def process_data(pitches, yaws, readings):
    """
    Converts the recorded positions in spherical coordinates (pitch, yaw, radius)
    into Cartesian coords (x, y ,z) for displaying.

    Args:
        pitches (list[float]): list of pitch values, in radians
        yaws (list[float]): list of yaw values, in radians
        readings (list[float]): list of distances, in centimeters

    Returns:
        cartesian_arr (np.ndarray): Array of points in cartesian coords
        spherical_arr (np.ndarray): Array of points in spherical coords
    """
    pitches, yaws, readings_dist = reading_to_dist(pitches, yaws, readings)

    spherical_arr = np.zeros((len(readings_dist), 3))
    cartesian_arr = np.zeros((len(readings_dist), 3))

    spherical_arr[:, 0] = np.array(pitches)
    spherical_arr[:, 1] = np.array(yaws)
    spherical_arr[:, 2] = np.array(readings_dist)

    # Convert spherical coordinates to cartesian coordinates using sin and cos
    cartesian_arr[:, 0] = (
        spherical_arr[:, 2] * np.cos(spherical_arr[:, 1]) * np.cos(spherical_arr[:, 0])
    )
    cartesian_arr[:, 1] = (
        spherical_arr[:, 2] * np.sin(spherical_arr[:, 1]) * np.cos(spherical_arr[:, 0])
    )
    cartesian_arr[:, 2] = spherical_arr[:, 2] * np.sin(spherical_arr[:, 0])

    return cartesian_arr, spherical_arr


def display_data(data):
    """
    Displays the provided data in a 3d scatter plot and saves it to a csv

    Args:
        data (np.ndarray): data points to plot, where each data point
        is a row and x,y,z correspond to columns 0, 1, and 2
    """
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    # Save cartesian data to csv
    np.savetxt("recorded_scan.csv", data, delimiter=",")

    # Plot data in 3d scatter plot with color corresponding to dist
    ax.scatter(
        data[:, 0],
        data[:, 1],
        data[:, 2],
        c=data[:, 0] ** 2 + data[:, 1] ** 2 + data[:, 2] ** 2, 
        cmap="plasma",
    )

    # Set up plot attributes
    ax.axis("equal")
    ax.set_xlabel("x (cm)")
    ax.set_ylabel("y (cm)")
    ax.set_zlabel("z (cm)")
    ax.set_title("Scan results in three dimensions")
    plt.show()


def spoof_data():
    """
    Tests the polar -> cartesian mapping by generating data in the shape
    of a sphere. Every point has distance 1 from the origin.

    Returns:
        a numpy ndarray in the shape (50,3)
    """
    pitches = []
    yaws = []
    readings = []

    # Spoof sensor data; should generate a sphere
    # of constant distance from the origin
    for i in range(50):
        for j in range(50):
            pitches.append(i * np.pi / 180)
            yaws.append(j * np.pi / 180)
            readings.append(1)

    print(f"readings: {readings}")
    processed, _ = process_data(pitches, yaws, readings)
    display_data(processed)


def init_connection():
    """
    Initialize serial connection with a port specified by the first argument
    passed when calling the python file.
    """
    print("hi")
    port = "/dev/cu.usbmodem1051DB37DE2C2"
    if len(sys.argv) > 1:
        port = sys.argv[1]
    cxn = Serial(port, baudrate=9600)
    cxn.write([int(1)])
    return cxn


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "0":
        print("spoofing data")
        spoof_data()
    else:
        main()
