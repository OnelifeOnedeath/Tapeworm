#!/usr/bin/env python3
"""
Tapeworm Web Interface 🐛
Web-версия визуализатора Brainfuck
"""

import streamlit as st
import sys
import os
import time

# Добавляем путь чтобы импортировать tapeworm
sys.path.append(os.path.dirname(__file__))

try:
    from tapeworm import Tapeworm
except ImportError:
    st.error("❌ Не удалось импортировать модуль tapeworm")
    st.stop()

def main():
    st.set_page_config(
        page_title="Tapeworm 🐛",
        page_icon="🐛",
        layout="wide"
    )
    
    st.title("🐛 Tapeworm - Brainfuck Visualizer")
    st.markdown("**Смотри как твой код ползет по памяти!**")
    
    # Боковая панель с настройками
    with st.sidebar:
        st.header("⚙️ Настройки")
        tape_size = st.slider("Размер ленты", 10, 100, 30)
        max_steps = st.number_input("Макс. шагов", 100, 100000, 5000)
        speed = st.slider("Скорость (мс)", 10, 1000, 200)
        
        st.markdown("---")
        st.markdown("### 📝 Примеры кода")
        if st.button("Hello World"):
            st.session_state.code = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
        if st.button("Простой счетчик"):
            st.session_state.code = "+++[>+++<-]>. "
    
    # Основная область
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🧠 Brainfuck код")
        
        # Инициализируем код в session_state если его нет
        if 'code' not in st.session_state:
            st.session_state.code = "++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++."
        
        code_input = st.text_area(
            "Введи Brainfuck код:",
            height=300,
            key="code",
            label_visibility="collapsed"
        )
        
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            if st.button("🚀 Выполнить", type="primary", use_container_width=True):
                if code_input.strip():
                    execute_bf(code_input.strip(), tape_size, max_steps, speed, col2)
                else:
                    st.warning("Введите Brainfuck код!")
        
        with col1_2:
            if st.button("🔄 Сбросить", use_container_width=True):
                st.rerun()
    
    with col2:
        st.subheader("👀 Визуализация")
        if 'execution_done' not in st.session_state:
            st.info("Нажмите '🚀 Выполнить' для запуска визуализации")
            st.image("https://via.placeholder.com/400x200/4A90E2/FFFFFF?text=Tapeworm+Visualizer", 
                    caption="Здесь будет отображаться выполнение кода")

def execute_bf(code, tape_size, max_steps, speed, output_col):
    """Выполняет Brainfuck код и показывает визуализацию"""
    
    with output_col:
        st.subheader("🎯 Выполнение")
        
        # Создаем интерпретатор
        try:
            worm = Tapeworm(tape_size)
            clean_code = ''.join(c for c in code if c in '><+-.,[]')
            if not clean_code:
                st.error("❌ Код не содержит валидных Brainfuck команд!")
                return
                
            worm.load_code(clean_code)
        except Exception as e:
            st.error(f"❌ Ошибка загрузки кода: {e}")
            return
        
        # Контейнеры для вывода
        output_container = st.empty()
        tape_container = st.empty()
        step_container = st.empty()
        progress_bar = st.progress(0)
        
        steps = 0
        output_text = ""
        
        # Плейсхолдер для анимации
        with st.expander("📊 Детали выполнения", expanded=True):
            details_placeholder = st.empty()
        
        # Выполняем пошагово
        while steps < max_steps:
            state = worm.step()
            if state is None:
                break
                
            # Обновляем вывод
            current_output = ''.join(worm.output_buffer)
            if current_output != output_text:
                output_text = current_output
                output_container.markdown(f"**📤 Вывод:** `{output_text}`")
            
            # Визуализация ленты
            tape_html = render_tape(state['after']['tape'], state['after']['pointer'], show_cells=tape_size)
            tape_container.markdown(tape_html, unsafe_allow_html=True)
            
            # Информация о шаге
            step_info = f"""
            **Шаг {steps}:** 
            - Команда: `{state['command']}`
            - Позиция: {state['position']}
            - Указатель: {state['after']['pointer']}
            """
            step_container.markdown(step_info)
            
            # Детали выполнения
            details_text = f"""
            ```brainfuck
{display_code_with_pointer(worm.code, state['position'])}
            ```
            """
            details_placeholder.markdown(details_text)
            
            # Прогресс
            progress = min(steps / max_steps, 1.0)
            progress_bar.progress(progress)
            
            steps += 1
            
            # Задержка для анимации
            time.sleep(speed / 1000)
        
        # Финальный результат
        st.success(f"✅ Выполнение завершено за **{steps}** шагов")
        st.balloons()
        
        if output_text:
            st.markdown(f"**🎉 Финальный вывод:** `{output_text}`")
        else:
            st.info("📝 Программа не вывела текст")
        
        # Сбрасываем прогресс
        progress_bar.empty()
        st.session_state.execution_done = True

def render_tape(tape, pointer, show_cells=20):
    """Генерирует HTML для визуализации ленты"""
    
    html = """
    <style>
    .tape-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 15px 0;
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
    .cell {
        width: 55px;
        height: 65px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        background: white;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .cell.active {
        border-color: #dc3545;
        background: linear-gradient(135deg, #ffe6e6, #ffcccc);
        box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
        transform: scale(1.05);
    }
    .cell-value {
        font-size: 16px;
        color: #212529;
        font-weight: 800;
    }
    .cell-address {
        font-size: 11px;
        color: #6c757d;
        margin-top: 4px;
    }
    .pointer {
        color: #dc3545;
        font-weight: bold;
        font-size: 12px;
        margin-top: 2px;
    }
    .cell-index {
        font-size: 10px;
        color: #adb5bd;
        margin-bottom: 2px;
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
            <div class="cell-index">{i}</div>
            <div class="cell-value">{value}</div>
            <div class="cell-address">'{char}'</div>
            {"<div class='pointer'>⬆</div>" if is_active else ""}
        </div>
        """
    
    html += "</div>"
    return html

def display_code_with_pointer(code, position):
    """Показывает код с указателем на текущую команду"""
    if position >= len(code):
        return code
    
    # Вставляем указатель под текущей командой
    lines = []
    current_line = ""
    
    for i, char in enumerate(code):
        current_line += char
        if i == position:
            # Добавляем строку с указателем
            lines.append(current_line)
            lines.append(" " * (len(current_line) - 1) + "^")
            current_line = ""
        elif len(current_line) >= 50:  # Перенос строки каждые 50 символов
            lines.append(current_line)
            current_line = ""
    
    if current_line:
        lines.append(current_line)
    
    return "\n".join(lines)

if __name__ == "__main__":
    main()
