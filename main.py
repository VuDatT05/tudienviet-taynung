import unicodedata
import json
import os
from flask import Flask, render_template, request

app = Flask(__name__)

# Đường dẫn tới file từ điển
DEFAULT_DICTIONARY_PATH = os.path.join(os.path.dirname(__file__), 'taydictionary.json')


def chuan_hoa_unicode(text):
    """Chuẩn hóa chuỗi Unicode để đảm bảo đồng nhất."""
    if text:
        return unicodedata.normalize('NFC', text.strip().lower())
    return ""


def tai_tu_dien():
    """Tải từ điển tích hợp sẵn từ file JSON."""
    try:
        if not os.path.exists(DEFAULT_DICTIONARY_PATH):
            return {}, f"File từ điển không tồn tại: {DEFAULT_DICTIONARY_PATH}"
        with open(DEFAULT_DICTIONARY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f), None
    except json.JSONDecodeError:
        return {}, f"File từ điển {DEFAULT_DICTIONARY_PATH} không đúng định dạng JSON."
    except Exception as e:
        return {}, f"Đã xảy ra lỗi khi tải từ điển: {str(e)}"


def dich_cau(cau, tu_dien):
    """
    Dịch cả câu ưu tiên cụm từ trong từ điển, nếu không có thì dịch từng từ.
    """
    cau_chuan = chuan_hoa_unicode(cau)  # Chuẩn hóa câu
    tu_da_dich = []
    tu_phan_tach = cau_chuan.split()  # Tách câu thành từng từ

    i = 0
    while i < len(tu_phan_tach):
        found = False
        # Thử dịch cụm từ từ dài nhất tới ngắn nhất
        for j in range(len(tu_phan_tach), i, -1):
            cum_tu = " ".join(tu_phan_tach[i:j])
            if cum_tu in tu_dien:
                tu_da_dich.append(tu_dien[cum_tu])  # Dịch cụm từ
                i = j  # Cập nhật vị trí để bỏ qua các từ đã xử lý
                found = True
                break
        if not found:
            # Nếu không tìm thấy cụm từ, giữ nguyên từ hiện tại
            tu_da_dich.append(tu_phan_tach[i])
            i += 1

    return " ".join(tu_da_dich)  # Ghép các từ/cụm từ đã dịch thành câu


@app.route('/', methods=['GET', 'POST'])
def index():
    ket_qua = ""
    if request.method == 'POST':
        cau_goc = request.form.get('text_input', '')
        tu_dien, error_msg = tai_tu_dien()

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
    tu_dien, error_msg = tai_tu_dien()

    if error_msg or not query:
        return {"suggestions": []}

    # Lọc danh sách từ trong từ điển bắt đầu bằng từ đã nhập
    suggestions = [tu for tu in tu_dien.keys() if tu.startswith(query)]

    # Giới hạn số lượng gợi ý, chỉ lấy tối đa 5 từ
    return {"suggestions": suggestions[:5]}  # Lấy tối đa 5 gợi ý


if __name__ == '__main__':
    if not os.path.exists(DEFAULT_DICTIONARY_PATH):
        print(f"File từ điển không tồn tại: {DEFAULT_DICTIONARY_PATH}. Vui lòng kiểm tra lại.")
    else:
        print(f"Sử dụng file từ điển: {DEFAULT_DICTIONARY_PATH}")
    app.run(debug=True)
