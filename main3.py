import unicodedata
import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Đường dẫn tới file từ điển
DEFAULT_DICTIONARY_PATH_VN_TN = os.path.join(os.path.dirname(__file__), 'taydictionary.json')  # Tiếng Việt → Tày-Nùng
DEFAULT_DICTIONARY_PATH_TN_VN = os.path.join(os.path.dirname(__file__), 'vietdictionary.json')  # Tày-Nùng → Tiếng Việt


def chuan_hoa_unicode(text):
    """Chuẩn hóa chuỗi Unicode để đảm bảo đồng nhất."""
    if text:
        return unicodedata.normalize('NFC', text.strip().lower())
    return ""


def tai_tu_dien(path):
    """Tải từ điển tích hợp sẵn từ file JSON."""
    try:
        if not os.path.exists(path):
            return {}, f"File từ điển không tồn tại: {path}"
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError:
        return {}, f"File từ điển {path} không đúng định dạng JSON."
    except Exception as e:
        return {}, f"Đã xảy ra lỗi khi tải từ điển: {str(e)}"


def dich_cau(cau, tu_dien):
    """Dịch cả câu bằng cách ghép từ trong từ điển."""
    cau_chuan = chuan_hoa_unicode(cau)  # Chuẩn hóa câu
    tu_da_dich = []

    for tu in cau_chuan.split():  # Tách câu thành từng từ
        tu_dich = tu_dien.get(tu, tu)  # Tìm từ trong từ điển, nếu không có giữ nguyên
        tu_da_dich.append(tu_dich)

    return " ".join(tu_da_dich)  # Ghép các từ đã dịch thành câu


@app.route('/', methods=['GET', 'POST'])
def index():
    ket_qua = ""
    if request.method == 'POST':
        cau_goc = request.form.get('text_input', '')
        chuc_nang = request.form.get('mode', 'vn_to_tn')  # Chế độ dịch (tiếng Việt → Tày-Nùng mặc định)

        if chuc_nang == 'tn_to_vn':
            tu_dien, error_msg = tai_tu_dien(DEFAULT_DICTIONARY_PATH_TN_VN)
        else:
            tu_dien, error_msg = tai_tu_dien(DEFAULT_DICTIONARY_PATH_VN_TN)

        if error_msg:
            ket_qua = error_msg
        elif cau_goc.strip() == "":
            ket_qua = "Vui lòng nhập văn bản cần dịch."
        else:
            ket_qua = dich_cau(cau_goc, tu_dien)

    return render_template('index.html', ket_qua=ket_qua)


@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip().lower()
    mode = request.args.get('mode', 'vn_to_tn')  # Chế độ dịch: vn_to_tn hoặc tn_to_vn

    # Chọn từ điển dựa trên chế độ
    if mode == 'tn_to_vn':
        tu_dien, error_msg = tai_tu_dien(DEFAULT_DICTIONARY_PATH_TN_VN)
    else:
        tu_dien, error_msg = tai_tu_dien(DEFAULT_DICTIONARY_PATH_VN_TN)

    if error_msg or not query:
        return {"suggestions": []}

    # Lọc danh sách từ trong từ điển bắt đầu bằng từ đã nhập
    suggestions = [tu for tu in tu_dien.keys() if tu.startswith(query)]

    # Giới hạn số lượng gợi ý, chỉ lấy tối đa 5 từ
    return {"suggestions": suggestions[:5]}  # Lấy tối đa 5 gợi ý


if __name__ == '__main__':
    app.run(debug=True)
