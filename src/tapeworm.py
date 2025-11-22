#!/usr/bin/env python3
import sys

class BrainfuckInterpreter:
    def __init__(self):
        self.tape = [0] * 30000  # Стандартный размер ленты
        self.pointer = 0
        self.code = ""
        self.ip = 0  # Instruction pointer
        self.input_buffer = []
        self.output_buffer = []
    
    def load_code(self, code):
        self.code = code
    
    def step(self):
        """Выполняет одну команду и возвращает состояние"""
        if self.ip >= len(self.code):
            return None
        
        cmd = self.code[self.ip]
        
        if cmd == '>':
            self.pointer += 1
        elif cmd == '<':
            self.pointer -= 1
        elif cmd == '+':
            self.tape[self.pointer] = (self.tape[self.pointer] + 1) % 256
        elif cmd == '-':
            self.tape[self.pointer] = (self.tape[self.pointer] - 1) % 256
        elif cmd == '.':
            self.output_buffer.append(chr(self.tape[self.pointer]))
        elif cmd == ',':
            if self.input_buffer:
                self.tape[self.pointer] = ord(self.input_buffer.pop(0))
        elif cmd == '[' and self.tape[self.pointer] == 0:
            # Пропустить до закрывающей ]
            depth = 1
            while depth > 0:
                self.ip += 1
                if self.code[self.ip] == '[': depth += 1
                if self.code[self.ip] == ']': depth -= 1
        elif cmd == ']' and self.tape[self.pointer] != 0:
            # Вернуться к открывающей [
            depth = 1
            while depth > 0:
                self.ip -= 1
                if self.code[self.ip] == ']': depth += 1
                if self.code[self.ip] == '[': depth -= 1
        
        self.ip += 1
        return {
            'tape': self.tape[:10],  # Первые 10 ячеек для отображения
            'pointer': self.pointer,
            'current_command': cmd,
            'output': ''.join(self.output_buffer)
        }

# Минимальный пример использования
if __name__ == "__main__":
    interpreter = BrainfuckInterpreter()
    interpreter.load_code("++>+++[<+>-]")  # Простой пример
    for _ in range(10):
        state = interpreter.step()
        if state:
            print(f"Command: {state['current_command']} | Pointer: {state['pointer']} | Tape: {state['tape']}")
