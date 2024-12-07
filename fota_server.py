import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import logging

# إعداد التطبيق
app = Flask(__name__)

# الإعدادات
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'hex'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 ميجابايت كحد أقصى

# تكوين التطبيق
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# إنشاء المجلد إذا لم يكن موجودًا
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# إعداد التسجيل
logging.basicConfig(
    filename='firmware_uploads.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)

def allowed_file(filename):
    """التحقق من صحة الملف"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """توليد اسم ملف فريد"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{filename}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # التحقق من وجود الملف
        if 'file' not in request.files:
            return jsonify({
                'status': 'error', 
                'message': 'لم يتم اختيار أي ملف'
            }), 400
        
        file = request.files['file']
        
        # التحقق من اسم الملف
        if file.filename == '':
            return jsonify({
                'status': 'error', 
                'message': 'لم يتم اختيار ملف'
            }), 400
        
        # التحقق من نوع الملف وحجمه
        if file and allowed_file(file.filename):
            # توليد اسم ملف فريد
            filename = generate_unique_filename(secure_filename(file.filename))
            
            # حفظ الملف
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # تسجيل عملية الرفع
            logging.info(f"تم رفع الملف: {filename}")
            
            # محاكاة إرسال الفيرموير (يمكنك استبدالها بالكود الفعلي)
            try:
                send_firmware_to_printer(file_path)
                return jsonify({
                    'status': 'success', 
                    'message': f'تم رفع الفيرموير {filename} بنجاح',
                    'filename': filename
                }), 200
            except Exception as e:
                # إذا فشل إرسال الفيرموير
                logging.error(f"خطأ في إرسال الفيرموير: {str(e)}")
                return jsonify({
                    'status': 'error', 
                    'message': 'فشل في إرسال الفيرموير'
                }), 500
        
        # إذا كان الملف غير مسموح به
        return jsonify({
            'status': 'error', 
            'message': 'نوع ملف غير مسموح به. يرجى رفع ملف .hex فقط'
        }), 400
    
    # عرض صفحة الرفع
    return render_template('upload.html')

def send_firmware_to_printer(file_path):
    """
    دالة محاكاة لإرسال الفيرموير للطابعة
    يجب استبدالها بالكود الفعلي للاتصال بالطابعة
    """
    # TODO: استبدل هذا بكود الاتصال الفعلي بالطابعة
    print(f"محاكاة إرسال الفيرموير من: {file_path}")
    
    # مثال على بعض التحققات
    if not os.path.exists(file_path):
        raise Exception("الملف غير موجود")
    
    # يمكنك إضافة المزيد من التحققات هنا
    # مثل التأكد من صحة محتوى الفيرموير

@app.errorhandler(413)
def request_entity_too_large(error):
    """معالجة الأخطاء المتعلقة بحجم الملف الكبير"""
    return jsonify({
        'status': 'error', 
        'message': 'حجم الملف كبير جدًا. الحد الأقصى 16 ميجابايت'
    }), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # هذا السطر يجب أن يكون في نهاية الملف
app = app