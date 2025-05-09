# robot control
# cenfra

from ollama import chat
import pyautogui
import time

# ------------------------------------------------------------
# robot interface
# ------------------------------------------------------------

# this interface redirects the llm control commands to either the
# simulation window or the real robot.
class RobotInterface:
    def __init__(self, simulation):
        self.simulation = simulation
        
    def perform_simulation(self, instruction_robot) -> None:        
        pyautogui.keyDown(instruction_robot)
        time.sleep(0.3)
        pyautogui.keyUp(instruction_robot)

    def perform_real(self, instruction_robot) -> None:
        pass

    def perform(self, instruction_robot) -> None:
        if self.simulation:
            self.perform_simulation(instruction_robot)
        else:
            self.perform_real(instruction_robot)

# ------------------------------------------------------------
# robot control
# ------------------------------------------------------------

class RobotControl:
    def __init__(self):
        self.interface = RobotInterface(simulation=True)

    def chat(self, message:str) -> str:
        response = chat(model="robot_control", messages=[{"role": "user", "content": message}], stream=False)
        return response["message"]["content"].strip()
        
    def run(self) -> None:
        while True:
            instruction_human = input("instruction input:")
            instruction_robot = self.chat(instruction_human)
            self.interface.perform(instruction_robot)

if __name__ == "__main__":
    instance = RobotControl()
    instance.run()
