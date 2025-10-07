import customtkinter as ctk
import hashlib
from tkinter import messagebox

# 词库
# 可修改，但长度必须是偶数
ALPHABET : list[str] = list("abcdefghijklmnopqrstuvwxyz") 

#----------进度----------
def set_progress_bar(value : float):
    progress_bar.set(value)
    root.update()

#----------运算----------
def turn_deflect(deflect : list[int], turn_extent) -> list[int]:
    # 实际数组不会被取余，为了让用户参数能达无限。因轮子的生成依赖初始偏移的数据，便不可限缩初始偏移的原值。
    deflect_carry = deflect.copy() # 用于计算实际数组所需的进位
    # 给复制数组取余
    for n in range(len(deflect_carry)):
        deflect_carry[n] = deflect_carry[n] % len(ALPHABET)
    deflect[0] += turn_extent
    deflect_carry[0] += turn_extent
    # 给实际数组进位
    for i in range(len(deflect) - 1): 
        carry : int = int(deflect_carry[i] / len(ALPHABET)) # 进位
        deflect[i + 1] += carry
        deflect_carry[i + 1] += carry
    return deflect

def character_conversion(trans : list[str], letter : str) -> str:
    for trans_character in trans:
        if letter in trans_character:
            letter_index = trans_character.index(letter)
            letter = trans_character[(letter_index + 1) % 2] #0->1, 1->0
    return letter

def unrest_alphabet(init_value : str) -> list[str]:
    alphabet_list : list[str] = ALPHABET.copy()
    random_numbers : list[int] = []
    for n in range(len(alphabet_list)):
        parameter : str = init_value + str(len(init_value) * (len(init_value) - n))
        hash_object = hashlib.sha3_512(parameter.encode("utf-8"))
        hash_bytes = hash_object.digest()
        hash_int : int = int.from_bytes(hash_bytes, byteorder='big')
        random_numbers.append(hash_int)

    # 使用Fisher-Yates洗牌算法来打乱字符串
    for i in range(len(alphabet_list) - 1, 0, -1):
        j = random_numbers[i] % (i + 1)
        alphabet_list[i], alphabet_list[j] = alphabet_list[j], alphabet_list[i]

    return alphabet_list

def generate_rotors(deflect : list[int] , turn_extent : int, user_character_trans : str,):
    rotors : list[list[str]] = []
    for i, deflect_value in enumerate(deflect):
        user_value_count : int = sum(deflect) * len(deflect) + deflect_value + turn_extent + i
        init_value : str = user_character_trans + str(user_value_count)
        alphabet_unrest = unrest_alphabet(init_value)
        rotors.append(alphabet_unrest)
    trans_init_value = ''.join(''.join(row) for row in rotors)
    machine_trans_parameter : list[str] = unrest_alphabet(trans_init_value)
    return rotors, machine_trans_parameter

def transduction(deflect : list[int], turn_extent : int, user_character_trans : list[str], text : str) -> str:
    user_trans_integration : str = "".join(user_character_trans)
    result : str = ""
    ignore_character : int = 0
    for letter in text:
        letter = letter.lower()
        if letter not in ALPHABET:
            result += letter
            ignore_character += 1
            set_progress_bar(len(result)/len(text))
            continue
        # 用户交替
        letter = character_conversion(user_character_trans, letter)
        rotors, machine_trans_parameter = generate_rotors(deflect, turn_extent, user_trans_integration)
        # 正向
        for n, rotor in enumerate(rotors):
            index_alphabet = ALPHABET.index(letter)
            index_deflect = (index_alphabet + deflect[n]) % len(ALPHABET)
            letter_index = rotor.index(ALPHABET[index_deflect])
            letter = ALPHABET[letter_index]
        # 机械交替
        machine_trans : list[str] = [machine_trans_parameter[l:l+2] for l in range(0, len(machine_trans_parameter), 2)]
        letter = character_conversion(machine_trans, letter)
        # 逆向
        for n in reversed(range(len(rotors))):
            index_alphabet = ALPHABET.index(letter)
            rotor_letter = rotors[n][index_alphabet]
            rotor_letter_index = ALPHABET.index(rotor_letter)
            index_deflect = (rotor_letter_index - deflect[n]) % len(ALPHABET)
            letter = ALPHABET[index_deflect]
        # 用户交替
        letter = character_conversion(user_character_trans, letter)
        deflect = turn_deflect(deflect, turn_extent)
        result += letter
        set_progress_bar(len(result)/len(text))
    return result

#----------参数处理----------
def get_user_input():
    text : str = text_user.get("1.0", "end").strip()
    turn_extent : str = turn_extent_entry.get().strip().replace(" ", "")
    user_character_trans : list[str] = trans_entry.get().lower().strip().replace(" ", "").split(",")
    deflect : list[str] = deflect_entry.get().strip().replace(" ", "").split(",")
    return deflect, turn_extent, user_character_trans, text

def process_user_parameter(deflect : list[str], turn_extent : str):
    processed_turn_extent : int = int(turn_extent)
    processed_deflect : list[int] = [int(n) for n in deflect]
    return processed_deflect, processed_turn_extent

def can_str_to_int(value) -> bool:
    try:
        value = int(value)
        return True
    except ValueError:
        return False

def error(info : str):
    messagebox.showerror("错误",info)
    return False

def check_user_parameter(deflect : list[str], turn_extent : str, user_character_trans : list[str]) -> bool:
    # 有填与否
    merged_str_parameter : str = ''.join(deflect) + turn_extent
    if merged_str_parameter == '':
        return error("请输入参数。")
    # 类型转换
    for d in deflect:
        if d == '': return error("初始偏移：请输入参数。")
        elif not can_str_to_int(d): return error("初始偏移：数值错误。")
    if turn_extent == '': return error("转动强度：请输入参数")
    elif not can_str_to_int(turn_extent): return error("转动强度：数值错误。")
    # 格式问题
    if user_character_trans[0] != '':
        if len(user_character_trans) > int(len(ALPHABET) / 2):
            return error("字符转换：参数过多，可能包含重复或不受支持的字符。")
        for i in user_character_trans:
            if len(i) != 2: return error("字符转换：转换必须于两个字符之间。")
            for n in i:
                if n not in ALPHABET: return error("字符转换：含不支持字符。")
                for c in user_character_trans:
                    if c == i: continue
                    if n in c: return error("字符转换：含重复字符。")
    return True

def processing(processing : bool):
    if processing:
        root.config(cursor="watch")
        text_user.configure(cursor="watch",state = "disabled")
        deflect_entry.configure(state = "disabled")
        turn_extent_entry.configure(state = "disabled")
        trans_entry.configure(state = "disabled")
        transduction_button.configure(state = "disabled")
        set_progress_bar(0)
    else:
        root.config(cursor="arrow")
        text_user.configure(cursor="xterm",state = "normal")
        deflect_entry.configure(state = "normal")
        turn_extent_entry.configure(state = "normal")
        trans_entry.configure(state = "normal")
        transduction_button.configure(state = "normal")
        set_progress_bar(1)

def transduction_main():
    deflect, turn_extent, user_character_trans, text = get_user_input()
    if check_user_parameter(deflect, turn_extent, user_character_trans) == False:
        return
    processing(True)
    deflect, turn_extent = process_user_parameter(deflect, turn_extent)
    transduction_text = transduction(deflect, turn_extent, user_character_trans, text).strip()
    text_user.configure(cursor="watch",state = "normal")
    text_user.delete("1.0", "end")
    text_user.insert("1.0",transduction_text)
    processing(False)
    messagebox.showinfo("完成","转密完成。")

def check_machine_parameter() -> bool:
    if len(ALPHABET) % 2 == 1:
        messagebox.showerror("配置错误","程序字符库长度为奇数。")
        root.destroy()

#----------部件布置----------
root = ctk.CTk()
root.title(f"Enigma+ 字符库长度:{len(ALPHABET)}")
root.geometry("520x720")
root.resizable(0,0)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

MONOSPACE_FONT = ("Monospace", 16)

deflect_entry = ctk.CTkEntry(
    root,
    font=MONOSPACE_FONT,
    placeholder_text="初始偏移（示例：1,2,3,4）",
    width=370,
    height=40,
    border_width=2,
    corner_radius=10
)
turn_extent_entry = ctk.CTkEntry(
    root,
    font=MONOSPACE_FONT,
    placeholder_text="转动强度",
    width=90,
    height=40,
    border_width=2,
    corner_radius=10
)
trans_entry = ctk.CTkEntry(
    root,
    font=MONOSPACE_FONT,
    placeholder_text="字符转换（示例：ab,cd,ef）",
    width=470,
    height=40,
    border_width=2,
    corner_radius=10
)
text_user = ctk.CTkTextbox(root, font=MONOSPACE_FONT, width=470, height=470)
progress_bar = ctk.CTkProgressBar(root, width=470, height=15, corner_radius=4)

transduction_button = ctk.CTkButton(
    root,
    font=MONOSPACE_FONT,
    text="转密",
    width=470,
    height=60,
    corner_radius=10,
    command=transduction_main
)
deflect_entry.place(x = 25,y = 25)
turn_extent_entry.place(x = 405,y = 25)
trans_entry.place(x=25,y=75)
text_user.place(x=25,y=130)
transduction_button.place(x=25,y=635)
progress_bar.place(x=25,y=610)
set_progress_bar(1)
check_machine_parameter()

root.mainloop()
