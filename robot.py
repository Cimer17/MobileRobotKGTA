import serial
import time


class Robots():
    
    def __init__(self):   
        self.ser = serial.Serial('/dev/cu.usbserial-120', 9600)  
        time.sleep(2)
        self.ser.reset_input_buffer()
    
    def robot_movement(self, command):
        if command == 'forward':
            self.ser.write(b'F')
        elif command == 'stop':
            self.ser.write(b'S')
        elif command == 'right':
            self.ser.write(b'R')
        elif command == 'back':
            self.ser.write(b'B')
        elif command == 'left':
            self.ser.write(b'L')
 
    def container_opening(self, command):
        if command == 'ON':
            self.ser.write(b'O')
        elif command == 'OFF':
            self.ser.write(b'N')


if __name__ == '__main__':
    robot = Robots()
    while True:
        command = input('Выберите команду - stop/forward/left/right:')
        if command is not None:
            robot.container_opening(command)
            print(f'Команда - {command} ')
        else:
            continue