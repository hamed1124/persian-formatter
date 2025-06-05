import os
import arabic_reshaper
from bidi.algorithm import get_display

# نام پوشه‌های ورودی و خروجی
INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

def process_line_for_game(line):
    """
    این تابع یک خط از فایل yml را پردازش می‌کند، بخش فارسی را پیدا کرده،
    آن را به فرمت بصری مخصوص بازی تبدیل می‌کند و خط جدید را برمی‌گرداند.
    """
    # برای جلوگیری از پردازش خطوطی که متن ندارند (مانند خطوط خالی یا کامنت‌ها)
    if ':' not in line or '"' not in line:
        return line

    # جدا کردن کلید (key) و مقدار (value)
    parts = line.split(':', 1)
    key = parts[0]
    value_part = parts[1]

    # پیدا کردن متن داخل دابل کوتیشن " "
    start_quote_index = value_part.find('"')
    end_quote_index = value_part.rfind('"')

    if start_quote_index != -1 and end_quote_index > start_quote_index:
        # استخراج متن اصلی (ممکن است حاوی متغیرهای بازی مثل $VAR$ باشد)
        text_to_format = value_part[start_quote_index + 1 : end_quote_index]
        
        # اگر متن خالی است یا فقط حاوی متغیر است، کاری انجام نده
        if not text_to_format.strip():
            return line

        # 1. شکل‌دهی حروف فارسی به حالت چسبان
        reshaped_text = arabic_reshaper.reshape(text_to_format)
        
        # 2. برعکس کردن ترتیب نمایش برای سیستم‌های چپ-به-راست
        bidi_text = get_display(reshaped_text)
        
        # بازسازی خط با مقدار فرمت شده
        # بخش‌های قبل و بعد از کوتیشن‌ها حفظ می‌شوند (برای حفظ فاصله‌ها و ...)
        before_quote = value_part[:start_quote_index + 1]
        after_quote = value_part[end_quote_index:]
        
        new_value_part = f"{before_quote}{bidi_text}{after_quote}"
        
        return f"{key}:{new_value_part}"
        
    return line

def main():
    # --- ساخت پوشه‌ها در صورت عدم وجود ---
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"پوشه '{INPUT_FOLDER}' ساخته شد. لطفاً فایل‌های ترجمه شده با فرمت فارسی نرمال را در آن قرار دهید.")
        return
        
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # --- پیدا کردن فایل‌ها برای پردازش ---
    try:
        files_to_process = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.yml')]
    except FileNotFoundError:
        print(f"خطا: پوشه ورودی '{INPUT_FOLDER}' یافت نشد.")
        return

    if not files_to_process:
        print(f"هیچ فایل .yml در پوشه '{INPUT_FOLDER}' برای پردازش یافت نشد.")
        return

    print(f"تعداد {len(files_to_process)} فایل برای پردازش یافت شد...")

    # --- شروع فرآیند تبدیل ---
    for filename in files_to_process:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)
        
        print(f"درحال پردازش فایل: {filename} ...")
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f_in, \
                 open(output_path, 'w', encoding='utf-8') as f_out:
                
                for line in f_in:
                    processed_line = process_line_for_game(line)
                    f_out.write(processed_line)
        except Exception as e:
            print(f"خطایی هنگام پردازش فایل {filename} رخ داد: {e}")

    print("\nپردازش تمام فایل‌ها با موفقیت به پایان رسید.")
    print(f"فایل‌های نهایی در پوشه '{OUTPUT_FOLDER}' ذخیره شدند.")

if __name__ == "__main__":
    main()
