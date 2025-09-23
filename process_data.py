"""

"""
import sys
import matplotlib.pyplot as plt
import numpy as np
from serial import Serial, SerialException

def main():
    cxn = init_connection()

    pitch_list = []
    yaw_list = []
    reading_list = []

    while cxn.inWaiting() < 1:
        pass

    while (True):
        result = cxn.readline().decode('ascii').strip()

        if len(result) < 1:
            continue

        print(type(result))
        print(result)
        result_split = result.split(",")

        if len(result_split) < 3 or '' in result_split:
            continue

        print(result_split)
        if '-1' in result_split:
            break
        print(type(result_split[0]))
        pitch_list.append(float(result_split[0])*np.pi / 180)
        yaw_list.append(float(result_split[1])*np.pi / 180)
        reading_list.append(result_split[2])
        print(f"Decoded: {result}, reading: {result_split[2]}")

    processed,unprocessed = process_data(pitch_list,yaw_list,reading_list)
    display_data(processed)

def voltage_to_dist(readings):
    """
    Use the provided transfer function of the sensor to convert voltage readings
    into distances
    """
    ### Exact points estimated from graphed transfer function
    dist_list = []
    for reading in readings:
        if reading > 0.4 and reading < 2.0:
            voltage = reading * (5 / 1024)
            dist_list.append(1/((1/60)*voltage))

def process_data(pitches,yaws,readings):
    """
    Converts the recorded positions in spherical coordinates (pitch, yaw, radius)
    into Cartesian coords (x, y ,z) for displaying. 
    """
    spherical_arr = np.zeros((len(readings),3))
    cartesian_arr = np.zeros((len(readings),3))

    spherical_arr[:,0] = np.array(pitches)
    spherical_arr[:,1] = np.array(yaws)
    spherical_arr[:,2] = np.array(readings)

    cartesian_arr[:,0] = spherical_arr[:,2] * np.cos(spherical_arr[:,1]) * np.cos(spherical_arr[:,0])
    cartesian_arr[:,1] = spherical_arr[:,2] * np.sin(spherical_arr[:,1]) * np.cos(spherical_arr[:,0])
    cartesian_arr[:,2] = spherical_arr[:,2] * np.sin(spherical_arr[:,0])

    return cartesian_arr,spherical_arr

def display_data(data):
    """

    """
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.scatter(data[:,0],data[:,1],data[:,2])
    ax.axis('equal')
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
    for i in range(50):
        for j in range(50):
            pitches.append(i*np.pi/180)
            yaws.append(j*np.pi/180)
            readings.append(1)

    print(f"readings: {readings}")
    processed,unprocessed = process_data(pitches,yaws,readings)
    display_data(processed)

def init_connection():
    """
    Initialize serial connection with a port specified by the first argument
    passed when calling the python file. 
    """
    port = "/dev/cu.usbmodem1051DB37DE2C2"
    if len(sys.argv) > 1:
        port = sys.argv[1]
    cxn = Serial(port,baudrate=9600)
    cxn.write([int(1)])
    return cxn

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == '0':
        print("spoofing data")
        spoof_data()
    else:
        main()
