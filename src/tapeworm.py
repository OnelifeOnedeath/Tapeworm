#!/usr/bin/env python3
"""
Tapeworm - Визуализатор выполнения Brainfuck
🐛 Смотри как твой код ползет по памяти!
"""

import sys
import os

class Tapeworm:
    def __init__(self, tape_size=30000):
        self.tape = [0] * tape_size  # Лента памяти
        self.pointer = 0              # Указатель на текущую ячейку
        self.code = ""                # Brainfuck код
        self.ip = 0                   # Счетчик команд (Instruction Pointer)
        self.input_buffer = []        # Буфер ввода
        self.output_buffer = []       # Буфер вывода
        self.bracket_map = {}         # Карта скобок для циклов
        
    def load_code(self, code):
        """Загружает и проверяет Brainfuck код"""
        self.code = code
        self._build_bracket_map()
        
    def _build_bracket_map(self):
        """Строит карту скобок для обработки циклов"""
        stack = []
        for i, cmd in enumerate(self.code):
            if cmd == '[':
                stack.append(i)
            elif cmd == ']':
                if not stack:
                    raise SyntaxError(f"Непарная ']' на позиции {i}")
                start = stack.pop()
                self.bracket_map[start] = i
                self.bracket_map[i] = start
        if stack:
            raise SyntaxError(f"Непарная '[' на позиции {stack[-1]}")
    
    def step(self):
        """Выполняет одну команду и возвращает состояние"""
        if self.ip >= len(self.code):
            return None
            
        cmd = self.code[self.ip]
        
        # Состояние ДО выполнения команды
        state_before = {
            'tape': self.tape.copy(),
            'pointer': self.pointer,
            'current_command': cmd,
            'command_position': self.ip,
            'output': ''.join(self.output_buffer)
        }
        
        try:
            # ВЫПОЛНЕНИЕ КОМАНД
            if cmd == '>':
                self.pointer += 1
                if self.pointer >= len(self.tape):
                    self.tape.append(0)  # Расширяем ленту если нужно
            elif cmd == '<':
                self.pointer -= 1
                if self.pointer < 0:
                    raise MemoryError("Указатель ушел в отрицательную зону")
            elif cmd == '+':
                self.tape[self.pointer] = (self.tape[self.pointer] + 1) % 256
            elif cmd == '-':
                self.tape[self.pointer] = (self.tape[self.pointer] - 1) % 256
            elif cmd == '.':
                char = chr(self.tape[self.pointer])
                self.output_buffer.append(char)
                print(char, end='', flush=True)
            elif cmd == ',':
                if self.input_buffer:
                    self.tape[self.pointer] = ord(self.input_buffer.pop(0))
                else:
                    # Если нет входных данных, используем 0
                    self.tape[self.pointer] = 0
            elif cmd == '[' and self.tape[self.pointer] == 0:
                # Перепрыгиваем вперед до закрывающей ]
                self.ip = self.bracket_map[self.ip]
            elif cmd == ']' and self.tape[self.pointer] != 0:
                # Возвращаемся назад к открывающей [
                self.ip = self.bracket_map[self.ip]
                
        except Exception as e:
            print(f"\nОшибка выполнения команды '{cmd}' на позиции {self.ip}: {e}")
            return None
            
        self.ip += 1  # Переходим к следующей команде
        
        # Возвращаем полное состояние ДО и ПОСЛЕ
        return {
            'before': state_before,
            'after': {
                'tape': self.tape.copy(),
                'pointer': self.pointer,
                'output': ''.join(self.output_buffer)
            },
            'command': cmd,
            'position': self.ip - 1
        }

    def get_state(self):
        """Возвращает текущее состояние для визуализации"""
        return {
            'tape': self.tape.copy(),
            'pointer': self.pointer,
            'ip': self.ip,
            'output': ''.join(self.output_buffer),
            'code': self.code
        }
    
    def run(self, max_steps=100000):
        """Запускает программу с базовой визуализацией"""
        print("🐛 Tapeworm выполняет Brainfuck код...")
        print("=" * 50)
        
        steps = 0
        while self.ip < len(self.code) and steps < max_steps:
            state = self.step()
            if state is None:
                break
                
            # Базовая визуализация - показываем первые 10 ячеек
            tape_preview = ' '.join(f'{val:3d}' for val in self.tape[:10])
            pointer_pos = state['before']['pointer']
            pointer_indicator = '   ' * pointer_pos + ' ^'
            
            print(f"Шаг {steps:4d}: [{state['command']}] | Лента: {tape_preview}")
            print(f"         {pointer_indicator}")
            
            steps += 1
            
        print("=" * 50)
        print(f"Выполнение завершено за {steps} шагов")
        print(f"Вывод: {''.join(self.output_buffer)}")
        
        return steps

def main():
    if len(sys.argv) != 2:
        print("Использование: python tapeworm.py <brainfuck_файл.bf>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            code = f.read()
        
        # Очищаем код от не-Brainfuck символов
        code = ''.join(c for c in code if c in '><+-.,[]')
        
        worm = Tapeworm()
        worm.load_code(code)
        worm.run()
        
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
