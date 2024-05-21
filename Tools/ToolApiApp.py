from flask import Flask, jsonify
from threading import Thread
import logging


class ToolApiApp(Flask):

    def __init__(self, name, port, command_dict):
        super().__init__(name)
        self.__command_dict = command_dict
        self.__port = port
    
    def __init_commands(self):
        """Initialize the commands"""
        for command in self.__command_dict:
            @self.route('/' + command, methods=['POST'])
            def execute_command():
                return self.__execute_command(command)

    def __execute_command(self, command):
        """Execute the command in a separate thread"""
        if command in self.__command_dict:
            logging.info("Executing command: " + command)
            Thread(target=self.__command_dict[command]).start()
            return jsonify({'message': command + ' started successfully.'}), 200
        else:
            return jsonify({'message': 'Invalid command: ' + command}), 400
    
    def run(self):
        self.__init_commands()
        self.run(port=self.__port)