import json
import os

# Đường dẫn file từ điển gốc và từ điển ngược
DEFAULT_DICTIONARY_PATH = 'taydictionary.json'
REVERSED_DICTIONARY_PATH = 'vietdictionary.json'


def tao_tu_dien_nguoc(input_path, output_path):
    """
    Tạo từ điển ngược từ file từ điển gốc.
    :param input_path: Đường dẫn file từ điển gốc (Tày-Nùng -> Tiếng Việt).
    :param output_path: Đường dẫn file từ điển ngược (Tiếng Việt -> Tày-Nùng).
    """
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File từ điển không tồn tại: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            original_dict = json.load(f)

        reversed_dict = {}
        for key, value in original_dict.items():
            # Nếu value đã tồn tại trong từ điển ngược, gộp key mới vào danh sách
            if value in reversed_dict:
                reversed_dict[value].append(key)
            else:
                reversed_dict[value] = [key]

        # Ghi từ điển ngược ra file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(reversed_dict, f, ensure_ascii=False, indent=4)
        print(f"Tạo từ điển ngược thành công tại: {output_path}")
    except Exception as e:
        print(f"Lỗi: {str(e)}")


# Tạo từ điển ngược
tao_tu_dien_nguoc(DEFAULT_DICTIONARY_PATH, REVERSED_DICTIONARY_PATH)
