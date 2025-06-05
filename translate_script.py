import os
import arabic_reshaper
from bidi.algorithm import get_display
import re

# نام پوشه‌های ورودی و خروجی
INPUT_FOLDER = 'input'
OUTPUT_FOLDER = 'output'

def process_line_for_game(line):
    """
    این تابع یک خط از فایل yml را پردازش می‌کند، بخش فارسی را پیدا کرده،
    آن را به فرمت بصری مخصوص بازی تبدیل می‌کند و خط جدید را برمی‌گرداند.
    """
    # برای جلوگیری از پردازش خطوطی که متن ندارند
    if ':' not in line or '"' not in line:
        return line

    # جدا کردن کلید و مقدار
    parts = line.split(':', 1)
    key = parts[0]
    value_part = parts[1].strip()

    # فقط مقادیر داخل دابل کوتیشن " " را پردازش می‌کنیم
    if value_part.startswith('"') and value_part.endswith('"'):
        # استخراج متن اصلی (ممکن است حاوی متغیرهای بازی مثل $VAR$ باشد)
        text_to_format = value_part[1:-1]
        
        # اگر متن خالی است، کاری انجام نده
        if not text_to_format.strip():
            return line

        # 1. شکل‌دهی حروف فارسی به حالت چسبان
        reshaped_text = arabic_reshaper.reshape(text_to_format)
        
        # 2. برعکس کردن ترتیب نمایش برای سیستم‌های چپ-به-راست
        bidi_text = get_display(reshaped_text)
        
        # بازسازی خط با مقدار فرمت شده
        # فضاهای خالی انتهای خط (مثل newline) را حفظ می‌کنیم
        trailing_whitespace = parts[1][len(parts[1].rstrip()):]
        return f'{key}: "{bidi_text}"{trailing_whitespace}'
        
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