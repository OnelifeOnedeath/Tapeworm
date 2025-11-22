#!/usr/bin/env python3
"""
Tapeworm Web Interface 🐛
Web-версия визуализатора Brainfuck
"""

import streamlit as st
import sys
import os
from tapeworm import Tapeworm

def main():
    st.set_page_config(
        page_title="Tapeworm 🐛",
        page_icon="🐛",
        layout="wide"
    )
    
    st.title("🐛 Tapeworm - Brainfuck Visualizer")
    st.markdown("Смотри как твой код ползет по памяти!")
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("Настройки")
        tape_size = st.slider("Размер ленты", 10, 100, 30)
        max_steps = st.number_input("Макс. шагов", 100, 100000, 10000)
        auto_play = st.checkbox("Автозапуск", value=False)
        speed = st.slider("Скорость (мс)", 10, 1000, 100)
    
    # Основная область
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Brainfuck код")
        code_input = st.text_area(
            "Введи Brainfuck код:",
            height=300,
            placeholder="++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
        )
        
        if st.button("🚀 Выполнить") or auto_play:
            if code_input:
                execute_bf(code_input, tape_size, max_steps, col2)
            else:
                st.warning("Введите Brainfuck код!")
    
    with col2:
        st.subheader("Визуализация")
        st.info("Запустите код для отображения визуализации")

def execute_bf(code, tape_size, max_steps, output_col):
    """Выполняет Brainfuck код и показывает визуализацию"""
    
    with output_col:
        st.subheader("Выполнение")
        
        # Создаем интерпретатор
        worm = Tapeworm(tape_size)
        worm.load_code(code)
        
        # Контейнер для вывода
        output_container = st.empty()
        tape_container = st.empty()
        step_container = st.empty()
        
        steps = 0
        output_text = ""
        
        # Выполняем пошагово
        while steps < max_steps:
            state = worm.step()
            if state is None:
                break
                
            # Обновляем вывод
            if state['before']['output'] != output_text:
                output_text = state['before']['output']
                output_container.code(f"Вывод: {output_text}")
            
            # Визуализация ленты
            tape_html = render_tape(state['after']['tape'], state['after']['pointer'])
            tape_container.markdown(tape_html, unsafe_allow_html=True)
            
            # Информация о шаге
            step_container.write(f"**Шаг {steps}:** Команда `{state['command']}`")
            
            steps += 1
            
            # Небольшая задержка для анимации
            if st._is_running:
                import time
                time.sleep(speed / 1000)
        
        st.success(f"✅ Выполнение завершено за {steps} шагов")
        st.code(f"Финальный вывод: {output_text}")

def render_tape(tape, pointer, show_cells=20):
    """Генерирует HTML для визуализации ленты"""
    
    html = """
    <style>
    .tape-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin: 10px 0;
        padding: 10px;
        background: #f0f0f0;
        border-radius: 5px;
    }
    .cell {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #ccc;
        border-radius: 3px;
        background: white;
        font-family: monospace;
        font-weight: bold;
    }
    .cell.active {
        border-color: #ff4444;
        background: #fff0f0;
    }
    .cell-value {
        font-size: 12px;
    }
    .cell-address {
        font-size: 10px;
        color: #666;
    }
    </style>
    
    <div class="tape-container">
    """
    
    for i in range(min(show_cells, len(tape))):
        is_active = i == pointer
        cell_class = "cell active" if is_active else "cell"
        
        # Отображаем значение и ASCII символ
        value = tape[i]
        char = chr(value) if 32 <= value <= 126 else '·'
        
        html += f"""
        <div class="{cell_class}">
            <div>
                <div class="cell-value">{value}</div>
                <div class="cell-address">{char}</div>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

if __name__ == "__main__":
    main()
