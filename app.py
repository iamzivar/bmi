# ایمپورت کتابخانه‌های مورد نیاز برای پروژه
from flask import Flask, render_template, request, send_from_directory, make_response, send_file  # فریم‌ورک اصلی وب
import os  # کار با فایل‌ها و پوشه‌ها در سیستم‌عامل
from werkzeug.utils import secure_filename  # امن‌سازی نام فایل‌های آپلودی
from reportlab.pdfgen import canvas  # ساخت فایل PDF
from reportlab.lib.pagesizes import A4  # تعیین اندازه صفحه PDF
from reportlab.pdfbase import pdfmetrics  # مدیریت فونت‌ها در PDF
from reportlab.pdfbase.ttfonts import TTFont  # افزودن فونت TrueType به PDF
from selenium import webdriver  # کنترل خودکار مرورگر برای گرفتن اسکرین‌شات
from selenium.webdriver.chrome.options import Options  # تنظیمات مرورگر کروم
from selenium.webdriver.chrome.service import Service  # سرویس‌دهی به مرورگر کروم
from selenium.webdriver.common.by import By  # انتخاب عناصر HTML در Selenium
from selenium.webdriver.support.ui import WebDriverWait  # انتظار برای بارگذاری عناصر در Selenium
from selenium.webdriver.support import expected_conditions as EC  # شرایط انتظار در Selenium
from webdriver_manager.chrome import ChromeDriverManager  # مدیریت خودکار درایور کروم
import pdfkit  # تبدیل HTML به PDF
from flask import send_file  # ارسال فایل به کاربر
import io  # کار با داده‌های باینری و حافظه موقت
from PIL import Image  # پردازش تصویر
import base64  # تبدیل داده‌ها به Base64
import matplotlib.pyplot as plt  # رسم نمودار
import uuid  # تولید شناسه یکتا برای فایل‌ها

# راه‌اندازی برنامه Flask و تنظیمات اولیه
app = Flask(__name__, static_url_path='/static', static_folder='static')  # ایجاد اپلیکیشن Flask با مسیر استاتیک
app.config['UPLOAD_FOLDER'] = 'uploads'  # تعیین پوشه آپلود فایل‌ها
app.config['SECRET_KEY'] = 'supersecretkey'  # کلید امنیتی برای مدیریت session

# ثبت فونت فارسی برای استفاده در فایل‌های PDF
pdfmetrics.registerFont(TTFont('Vazir', 'static/fonts/Vazirmatn-Medium.ttf'))  # ثبت فونت فارسی برای خروجی PDF

# اطمینان از وجود پوشه uploads برای ذخیره فایل‌های آپلودی
if not os.path.exists('uploads'):
    os.makedirs('uploads')  # اگر پوشه وجود ندارد، آن را بساز

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)  # ارسال فایل آپلود شده به کاربر

translations = {
    'fa': {
        'title': 'محاسبه BMI',
        'submit': 'ادامه',
        'result_title': 'نتیجه برای',
        'gender': 'جنسیت',
        'age': 'سن',
        'height': 'قد',
        'weight': 'وزن',
        'condition': 'بیماری‌های زمینه‌ای',
        'bmi': 'شاخص توده بدنی',
        'status': 'وضعیت',
        'status_under': 'کمبود وزن',
        'status_normal': 'طبیعی',
        'status_over': 'اضافه وزن',
        'status_obese': 'چاقی مفرط',
        'condition_none': 'بدون بیماری',
        'condition_diabetes': 'دیابت',
        'condition_hypertension': 'فشار خون بالا',
        'condition_heart_disease': 'بیماری قلبی',
        'condition_asthma': 'آسم',
        'condition_arthritis': 'آرتریت',
        'condition_kidney_disease': 'بیماری کلیوی',
        'condition_thyroid_disease': 'بیماری تیروئید',
        'bmi_chart_title': 'نمودار وضعیت BMI',
        'bmi_chart_label': 'وزن (کیلوگرم)',
        'bmi_chart_y_label': 'شاخص توده بدنی (BMI)',
        'advice_under_none': '''
            توصیه‌های تخصصی:
            - افزایش مصرف مغزیجات و روغن‌های سالم
            - ورزش‌های مقاومتی ۳ بار در هفته
            - مصرف مکمل‌های ویتامینی زیر نظر پزشک
            ''',
        'advice_normal_none': '''
            توصیه‌های تخصصی:
            - حفظ تنوع غذایی با هرم غذایی استاندارد
            - ترکیب ورزش هوازی و قدرتی
            - چکاپ ماهانه سلامت
            ''',
        'advice_over_none': '''
            توصیه‌های تخصصی:
            - کاهش مصرف کربوهیدرات‌های ساده
            - افزایش فعالیت روزانه (حداقل ۱۰۰۰۰ قدم)
            - استفاده از ترازوی هوشمند برای ردیابی
            ''',
        'advice_obese_none': '''
            توصیه‌های تخصصی:
            - مشاوره فوری با پزشک متخصص
            - ثبت روزانه کال bracesری دریافتی
            - ورزش تحت نظر مربی حرفه‌ای
            ''',
        'advice_under_diabetes': '''
            توصیه‌های تخصصی:
            - کنترل قند خون با رژیم کم‌کربوهیدرات
            - ورزش‌های سبک روزانه (پیاده‌روی ۳۰ دقیقه)
            - چکاپ منظم قند خون
            ''',
        'advice_normal_diabetes': '''
            توصیه‌های تخصصی:
            - رژیم غذایی با شاخص گلیسمی پایین
            - ورزش هوازی ۴ بار در هفته
            - مشاوره منظم با متخصص تغذیه
            ''',
        'advice_over_diabetes': '''
            توصیه‌های تخصصی:
            - کاهش وزن تدریجی با رژیم کم‌قند
            - ورزش‌های هوازی سبک (۵ جلسه در هفته)
            - پایش قند خون روزانه
            ''',
        'advice_obese_diabetes': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر پزشک
            - ورزش‌های کم‌فشار تحت نظارت مربی
            - کنترل دقیق قند خون
            ''',
        'advice_under_hypertension': '''
            توصیه‌های تخصصی:
            - کاهش مصرف نمک
            - ورزش‌های هوازی سبک (پیاده‌روی)
            - پایش فشار خون روزانه
            ''',
        'advice_normal_hypertension': '''
            توصیه‌های تخصصی:
            - رژیم غذایی DASH
            - ورزش هوازی ۵ بار در هفته
            - کاهش استرس با مدیتیشن
            ''',
        'advice_over_hypertension': '''
            توصیه‌های تخصصی:
            - رژیم کم‌نمک و کم‌چرب
            - ورزش‌های هوازی (۴۵ دقیقه، ۴ بار در هفته)
            - پایش منظم فشار خون
            ''',
        'advice_obese_hypertension': '''
            توصیه‌های تخصصی:
            - رژیم غذایی DASH تحت نظر پزشک
            - ورزش‌های کم‌فشار با نظارت مربی
            - کنترل فشار خون روزانه
            ''',
        'advice_under_heart_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌چرب
            - ورزش‌های سبک تحت نظر پزشک
            - چکاپ قلبی منظم
            ''',
        'advice_normal_heart_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی مدیترانه‌ای
            - ورزش‌های هوازی سبک (۴ بار در هفته)
            - پایش سلامت قلب
            ''',
        'advice_over_heart_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌کلسترول
            - ورزش‌های سبک تحت نظارت
            - چکاپ منظم قلبی
            ''',
        'advice_obese_heart_disease constriction': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر متخصص قلب
            - ورزش‌های کم‌فشار با نظارت مربی
            - پایش مداوم سلامت قلب
            ''',
        'advice_under_asthma': '''
            توصیه‌های تخصصی:
            - رژیم غذایی ضدالتهابی
            - ورزش‌های تنفسی و سبک
            - استفاده منظم از داروهای تجویز شده
            ''',
        'advice_normal_asthma': '''
            توصیه‌های تخصصی:
            - رژیم غذایی متعادل با سبزیجات
            - ورزش‌های هوازی سبک با کنترل تنفس
            - چکاپ منظم ریه‌ها
            ''',
        'advice_over_asthma': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌کالری و ضدالتهابی
            - ورزش‌های سبک با تمرکز بر تنفس
            - پایش وضعیت تنفسی
            ''',
        'advice_obese_asthma': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر پزشک
            - ورزش‌های کم‌فشار با نظارت
            - کنترل دقیق وضعیت تنفسی
            ''',
        'advice_under_arthritis': '''
            توصیه‌های تخصصی:
            - رژیم غذایی غنی از امگا-۳
            - ورزش‌های انعطاف‌پذیری سبک
            - مشاوره با فیزیوتراپیست
            ''',
        'advice_normal_arthritis': '''
            توصیه‌های تخصصی:
            - رژیم غذایی ضدالتهابی
            - ورزش‌های کم‌فشار مانند شنا
            - پایش منظم مفاصل
            ''',
        'advice_over_arthritis': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌کالری و ضدالتهابی
            - ورزش‌های آبی و کششی
            - مشاوره با متخصص روماتولوژی
            ''',
        'advice_obese_arthritis': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر پزشک
            - ورزش‌های کم‌فشار با نظارت
            - کاهش وزن برای کاهش فشار روی مفاصل
            ''',
        'advice_under_kidney_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌پروتئین و کم‌نمک
            - ورزش‌های سبک با نظارت پزشک
            - پایش عملکرد کلیه
            ''',
        'advice_normal_kidney_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کنترل‌شده برای کلیه
            - ورزش‌های هوازی سبک
            - چکاپ منظم کلیه
            ''',
        'advice_over_kidney_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌پروتئین و کم‌نمک
            - ورزش‌های کم‌فشار
            - پایش دقیق عملکرد کلیه
            ''',
        'advice_obese_kidney_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر متخصص کلیه
            - ورزش‌های کم‌فشار با نظارت
            - کنترل وزن و عملکرد کلیه
            ''',
        'advice_under_thyroid_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی غنی از ید (زیر نظر پزشک)
            - ورزش‌های سبک برای متابولیسم
            - پایش منظم تیروئید
            ''',
        'advice_normal_thyroid_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی متعادل
            - ورزش‌های هوازی و مقاومتی سبک
            - چکاپ منظم تیروئید
            ''',
        'advice_over_thyroid_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی کم‌کالری
            - ورزش‌های سبک برای متابولیسم
            - پایش هورمون‌های تیروئید
            ''',
        'advice_obese_thyroid_disease': '''
            توصیه‌های تخصصی:
            - رژیم غذایی تحت نظر متخصص غدد
            - ورزش‌های کم‌فشار با نظارت
            - کنترل وزن و هورمون‌های تیروئید
            ''',
        'plan_under_none': '''
            برنامه ۷ روزه:
            🥑 صبحانه: املت اسفناج + آووکادو
            🥜 میان‌وعده: مخلوط مغزیجات
            🍗 ناهار: مرغ گریل شده + برنج قهوه‌ای
            🥛 شام: سوپ عدس + نان سبوس‌دار
            ''',
        'plan_normal_none': '''
            برنامه ۷ روزه:
            🥚 صبحانه: نان تست + املت سبزیجات
            🍎 میان‌وعده: میوه فصل
            🥩 ناهار: استیک گوشت + سیب زمینی آبپز
            🥦 شام: سالاد پروتئینی + کینوا
            ''',
        'plan_over_none': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج و حمص
            🍤 ناهار: میگو گریل شده + سبزیجات بخارپز
            🥒 شام: سوپ مرغ و جو
            ''',
        'plan_obese_none': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + قارچ
            🥑 میان‌وعده: آووکادو با گردو
            🥩 ناهار: سینه بوقلمون + کدو اسپاگتی
            🥬 شام: ماهی سفید + بروکلی بخارپز
            ''',
        'plan_under_diabetes': '''
            برنامه ۷ روزه:
            🥚 صبحانه: سفیده تخم مرغ + سبزیجات
            🥜 میان‌وعده: بادام خام
            🍗 ناهار: مرغ گریل شده + سالاد سبز
            🥬 شام: ماهی بخارپز + بروکلی
            ''',
        'plan_normal_diabetes': '''
            برنامه ۷ روزه:
            🥗 صبحانه: جو دوسر + توت‌ها
            🍎 میان‌وعده: سیب
            🍤 ناهار: میگو + سبزیجات بخارپز
            🥦 شام: سالاد مرغ + کینوا
            ''',
        'plan_over_diabetes': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥕 میان‌وعده: هویج
            🥩 ناهار: بوقلمون گریل شده + سالاد
            🥬 شام: ماهی سفید + سبزیجات
            ''',
        'plan_obese_diabetes': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + اسفناج
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: مرغ بخارپز + کدو
            🥬 شام: ماهی + سبزیجات بخارپز
            ''',
        'plan_under_hypertension': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + میوه
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_hypertension': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_hypertension': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌نمک
            ''',
        'plan_obese_hypertension': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'plan_under_heart_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + توت‌ها
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_heart_disease': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_heart_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌چرب
            ''',
        'plan_obese_heart_disease': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'plan_under_asthma': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + توت‌ها
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_asthma': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_asthma': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌چرب
            ''',
        'plan_obese_asthma': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'plan_under_arthritis': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + توت‌ها
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_arthritis': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_arthritis': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌چرب
            ''',
        'plan_obese_arthritis': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'plan_under_kidney_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + میوه
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_kidney_disease': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_kidney_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌نمک
            ''',
        'plan_obese_kidney_disease': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'plan_under_thyroid_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: ماست کم‌چرب + توت‌ها
            🍎 میان‌وعده: سیب
            🍗 ناهار: مرغ گریل شده + سبزیجات
            🥬 شام: ماهی سفید + سالاد سبز
            ''',
        'plan_normal_thyroid_disease': '''
            برنامه ۷ روزه:
            🥚 صبحانه: تخم مرغ آبپز + سبزیجات
            🥜 میان‌وعده: بادام خام
            🥩 ناهار: گوشت بدون چربی + کینوا
            🥦 شام: سالاد مرغ + سبزیجات
            ''',
        'plan_over_thyroid_disease': '''
            برنامه ۷ روزه:
            🥗 صبحانه: اسموتی سبز + جو دوسر
            🥕 میان‌وعده: هویج
            🍤 ناهار: میگو بخارپز + سبزیجات
            🥬 شام: سوپ سبزیجات کم‌چرب
            ''',
        'plan_obese_thyroid_disease': '''
            برنامه ۷ روزه:
            🍳 صبحانه: سفیده تخم مرغ + سبزیجات
            🥑 میان‌وعده: آووکادو
            🍗 ناهار: بوقلمون گریل شده + کدو
            🥬 شام: ماهی سفید + سبزیجات بخارپز
            ''',
        'extra_tips': '''
            نکات کلیدی برای همه وضعیت‌ها:
            ✅ خواب ۷-۹ ساعته
            ✅ مصرف ۸ لیوان آب روزانه
            ❌ اجتناب از غذاهای فرآوری شده
            ''',
        'exercise_under_none': '''
            🏋️ روتین ورزشی:
            - تمرینات مقاومتی: ۳ ست ۱۵ تایی (دمبل سبک)
            - پیاده‌روی روزانه: ۳۰ دقیقه
        ''',
        'exercise_normal_none': '''
            🏋️ روتین ورزشی:
            - تمرینات کراس فیت: ۴ جلسه در هفته
            - شنا: ۲ بار در هفته
        ''',
        'exercise_over_none': '''
            🏋️ روتین ورزشی:
            - دوی استقامت: ۴۵ دقیقه ۳ بار در هفته
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_obese_none': '''
            🏋️ روتین ورزشی:
            - تمرینات اینتروال (HIIT): ۵ جلسه در هفته
            - تمرین با وزنه‌های سنگین زیر نظر مربی
        ''',
        'exercise_under_diabetes': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۳۰ دقیقه روزانه
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_normal_diabetes': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی: ۴ جلسه در هفته
            - تمرینات کششی: ۲ جلسه در هفته
        ''',
        'exercise_over_diabetes': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سریع: ۴۵ دقیقه، ۴ بار در هفته
            - تمرینات مقاومتی سبک: ۲ جلسه در هفته
        ''',
        'exercise_obese_diabetes': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۲ جلسه در هفته
        ''',
        'exercise_under_hypertension': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۳۰ دقیقه روزانه
            - یوگا: ۳ جلسه در هفته
        ''',
        'exercise_normal_hypertension': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی: ۵ جلسه در هفته
            - تمرینات کششی: ۲ جلسه در هفته
        ''',
        'exercise_over_hypertension': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سریع: ۴۵ دقیقه، ۴ بار در هفته
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_obese_hypertension': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۲ جلسه در هفته
        ''',
        'exercise_under_heart_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۲۰ دقیقه روزانه
            - تمرینات کششی: ۲ جلسه در هفته
        ''',
        'exercise_normal_heart_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی سبک: ۴ جلسه در هفته
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_over_heart_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سریع: ۳۰ دقیقه، ۴ بار در هفته
            - تمرینات مقاومتی سبک: ۲ جلسه در هفته
        ''',
        'exercise_obese_heart_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۲ جلسه در هفته
        ''',
        'exercise_under_asthma': '''
            🏋️ روتین ورزشی:
            - تمرینات تنفسی: ۱۵ دقیقه روزانه
            - پیاده‌روی سبک: ۲۰ دقیقه روزانه
        ''',
        'exercise_normal_asthma': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی سبک: ۴ جلسه در هفته
            - تمرینات تنفسی: ۳ جلسه در هفته
        ''',
        'exercise_over_asthma': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سریع: ۳۰ دقیقه، ۴ بار در هفته
            - یوگا با تمرکز بر تنفس: ۲ جلسه در هفته
        ''',
        'exercise_obese_asthma': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا با کنترل تنفس: ۲ جلسه در هفته
        ''',
        'exercise_under_arthritis': '''
            🏋️ روتین ورزشی:
            - تمرینات انعطاف‌پذیری: ۲۰ دقیقه روزانه
            - شنا: ۲ جلسه در هفته
        ''',
        'exercise_normal_arthritis': '''
            🏋️ روتین ورزشی:
            - ورزش‌های آبی: ۴ جلسه در هفته
            - تمرینات کششی: ۳ جلسه در هفته
        ''',
        'exercise_over_arthritis': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۳۰ دقیقه، ۴ بار در هفته
            - ورزش‌های آبی: ۲ جلسه در هفته
        ''',
        'exercise_obese_arthritis': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۳ جلسه در هفته
        ''',
        'exercise_under_kidney_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۲۰ دقیقه روزانه
            - تمرینات کششی: ۲ جلسه در هفته
        ''',
        'exercise_normal_kidney_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی سبک: ۴ جلسه در هفته
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_over_kidney_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۳۰ دقیقه، ۴ بار در هفته
            - تمرینات مقاومتی سبک: ۲ جلسه در هفته
        ''',
        'exercise_obese_kidney_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۲ جلسه در هفته
        ''',
        'exercise_under_thyroid_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سبک: ۲۰ دقیقه روزانه
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_normal_thyroid_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های هوازی سبک: ۴ جلسه در هفته
            - تمرینات مقاومتی سبک: ۲ جلسه در هفته
        ''',
        'exercise_over_thyroid_disease': '''
            🏋️ روتین ورزشی:
            - پیاده‌روی سریع: ۳۰ دقیقه، ۴ بار در هفته
            - یوگا: ۲ جلسه در هفته
        ''',
        'exercise_obese_thyroid_disease': '''
            🏋️ روتین ورزشی:
            - ورزش‌های کم‌فشار: ۵ جلسه در هفته
            - شنا: ۲ جلسه در هفته
        ''',
        # --- بیماری‌های جدید و توصیه‌ها (FA) ---
        'condition_cholesterol': 'چربی خون',
        'condition_anemia': 'کم‌خونی',
        'condition_depression': 'افسردگی',
        'condition_digestive_disorder': 'مشکلات گوارشی',
        'condition_osteoporosis': 'پوکی استخوان',
        # چربی خون
        'advice_normal_cholesterol': '''- کاهش مصرف چربی‌های اشباع\n- مصرف روغن زیتون و ماهی\n- پیاده‌روی روزانه''',
        'plan_normal_cholesterol': '''- صبحانه: جو دوسر + گردو\n- ناهار: ماهی کبابی + سبزیجات\n- شام: سوپ جو + سالاد سبز''',
        'exercise_normal_cholesterol': '''- پیاده‌روی سریع: ۳۰ دقیقه روزانه\n- دوچرخه‌سواری: ۲ بار در هفته''',
        'extra_tips_normal_cholesterol': '''- پرهیز از غذاهای سرخ‌شده\n- مصرف فیبر بالا''',
        'supplements_normal_cholesterol': '''- امگا ۳\n- فیبر محلول''',
        'warnings_normal_cholesterol': '''- پرهیز از مصرف زیاد تخم‌مرغ و گوشت قرمز\n- کنترل منظم چربی خون''',
        # کم‌خونی
        'advice_normal_anemia': '''- مصرف منابع آهن (گوشت قرمز، عدس)\n- مصرف ویتامین C همراه غذا\n- پرهیز از چای بعد غذا''',
        'plan_normal_anemia': '''- صبحانه: تخم مرغ + آب پرتقال\n- ناهار: خوراک عدس + گوشت\n- شام: سوپ اسفناج''',
        'exercise_normal_anemia': '''- پیاده‌روی سبک\n- یوگا''',
        'extra_tips_normal_anemia': '''- آزمایش خون منظم\n- مصرف مکمل آهن در صورت نیاز''',
        'supplements_normal_anemia': '''- آهن\n- ویتامین C''',
        'warnings_normal_anemia': '''- پرهیز از مصرف لبنیات همزمان با آهن\n- مشورت با پزشک''',
        # افسردگی
        'advice_normal_depression': '''- مصرف اسیدهای چرب امگا ۳\n- ورزش منظم\n- خواب کافی''',
        'plan_normal_depression': '''- صبحانه: نان سبوس‌دار + گردو\n- ناهار: ماهی سالمون + سبزیجات\n- شام: سوپ جو''',
        'exercise_normal_depression': '''- پیاده‌روی در طبیعت\n- مدیتیشن و یوگا''',
        'extra_tips_normal_depression': '''- ارتباط اجتماعی فعال\n- دوری از استرس''',
        'supplements_normal_depression': '''- امگا ۳\n- ویتامین D''',
        'warnings_normal_depression': '''- پرهیز از مصرف الکل\n- مشورت با روانپزشک''',
        # مشکلات گوارشی
        'advice_normal_digestive_disorder': '''- مصرف فیبر بالا\n- پرهیز از غذاهای چرب و سرخ‌شده\n- وعده‌های غذایی کوچک و متعدد''',
        'plan_normal_digestive_disorder': '''- صبحانه: ماست کم‌چرب + میوه\n- ناهار: برنج قهوه‌ای + سبزیجات بخارپز\n- شام: سوپ سبزیجات''',
        'exercise_normal_digestive_disorder': '''- پیاده‌روی آرام بعد غذا\n- حرکات کششی''',
        'extra_tips_normal_digestive_disorder': '''- نوشیدن آب کافی\n- پرهیز از پرخوری''',
        'supplements_normal_digestive_disorder': '''- پروبیوتیک\n- فیبر''',
        'warnings_normal_digestive_disorder': '''- پرهیز از مصرف نوشابه و فست‌فود\n- مشورت با متخصص گوارش''',
        # پوکی استخوان
        'advice_normal_osteoporosis': '''- مصرف لبنیات کم‌چرب\n- دریافت ویتامین D و کلسیم\n- ورزش‌های تحمل وزن''',
        'plan_normal_osteoporosis': '''- صبحانه: شیر کم‌چرب + نان سبوس‌دار\n- ناهار: خوراک مرغ + کلم بروکلی\n- شام: سوپ شیر''',
        'exercise_normal_osteoporosis': '''- پیاده‌روی تند\n- تمرینات مقاومتی''',
        'extra_tips_normal_osteoporosis': '''- قرار گرفتن در معرض نور خورشید\n- پرهیز از سیگار''',
        'supplements_normal_osteoporosis': '''- کلسیم\n- ویتامین D''',
        'warnings_normal_osteoporosis': '''- پرهیز از مصرف نوشابه\n- مشورت با پزشک''',
        # افزودن مقدار پیش‌فرض برای مکمل‌ها و هشدارها (FA)
        'supplements_default': 'با مشورت پزشک مکمل مناسب مصرف کنید.',
        'warnings_default': 'در صورت داشتن بیماری زمینه‌ای با پزشک مشورت کنید.'
    },
    'en': {
        'title': 'BMI Calculator',
        'submit': 'Continue',
        'result_title': 'Result for',
        'gender': 'Gender',
        'age': 'Age',
        'height': 'Height',
        'weight': 'Weight',
        'condition': 'Medical Conditions',
        'bmi': 'BMI',
        'status': 'Status',
        'status_under': 'Underweight',
        'status_normal': 'Normal',
        'status_over': 'Overweight',
        'status_obese': 'Obese',
        'condition_none': 'No Condition',
        'condition_diabetes': 'Diabetes',
        'condition_hypertension': 'Hypertension',
        'condition_heart_disease': 'Heart Disease',
        'condition_asthma': 'Asthma',
        'condition_arthritis': 'Arthritis',
        'condition_kidney_disease': 'Kidney Disease',
        'condition_thyroid_disease': 'Thyroid Disease',
        'bmi_chart_title': 'BMI Status Chart',
        'bmi_chart_label': 'Weight (kg)',
        'bmi_chart_y_label': 'Body Mass Index (BMI)',
        'advice_under_none': '''
            Professional Advice:
            - Increase nuts and healthy oils intake
            - Resistance training 3x/week
            - Vitamin supplements under medical supervision
            ''',
        'advice_normal_none': '''
            Professional Advice:
            - Follow standard food pyramid
            - Combine cardio & strength training
            - Monthly health checkups
            ''',
        'advice_over_none': '''
            Professional Advice:
            - Reduce simple carbohydrates
            - Increase daily steps (min 10,000)
            - Use smart scale for tracking
            ''',
        'advice_obese_none': '''
            Professional Advice:
            - Immediate consultation with specialist
            - Daily calorie logging
            - Exercise with professional trainer
            ''',
        'advice_under_diabetes': '''
            Professional Advice:
            - Control blood sugar with low-carb diet
            - Light daily exercise (30-min walk)
            - Regular blood sugar monitoring
            ''',
        'advice_normal_diabetes': '''
            Professional Advice:
            - Low glycemic index diet
            - Cardio exercise 4x/week
            - Regular nutritionist consultation
            ''',
        'advice_over_diabetes': '''
            Professional Advice:
            - Gradual weight loss with low-sugar diet
            - Light cardio exercises (5x/week)
            - Daily blood sugar monitoring
            ''',
        'advice_obese_diabetes': '''
            Professional Advice:
            - Diet under medical supervision
            - Low-impact exercises with trainer
            - Strict blood sugar control
            ''',
        'advice_under_hypertension': '''
            Professional Advice:
            - Reduce salt intake
            - Light aerobic exercise (walking)
            - Daily blood pressure monitoring
            ''',
        'advice_normal_hypertension': '''
            Professional Advice:
            - Follow DASH diet
            - Cardio exercise 5x/week
            - Stress reduction with meditation
            ''',
        'advice_over_hypertension': '''
            Professional Advice:
            - Low-salt, low-fat diet
            - Aerobic exercise (45 mins, 4x/week)
            - Regular blood pressure monitoring
            ''',
        'advice_obese_hypertension': '''
            Professional Advice:
            - DASH diet under medical supervision
            - Low-impact exercises with supervision
            - Daily blood pressure monitoring
            ''',
        'advice_under_heart_disease': '''
            Professional Advice:
            - Low-fat diet
            - Light exercise under medical supervision
            - Regular cardiac checkups
            ''',
        'advice_normal_heart_disease': '''
            Professional Advice:
            - Mediterranean diet
            - Light aerobic exercise (4x/week)
            - Heart health monitoring
            ''',
        'advice_over_heart_disease': '''
            Professional Advice:
            - Low-cholesterol diet
            - Light exercise with supervision
            - Regular cardiac checkups
            ''',
        'advice_obese_heart_disease': '''
            Professional Advice:
            - Diet under cardiologist supervision
            - Low-impact exercises with trainer
            - Continuous heart health monitoring
            ''',
        'advice_under_asthma': '''
            Professional Advice:
            - Anti-inflammatory diet
            - Light breathing exercises
            - Regular use of prescribed medications
            ''',
        'advice_normal_asthma': '''
            Professional Advice:
            - Balanced diet with vegetables
            - Light aerobic exercises with breathing control
            - Regular lung checkups
            ''',
        'advice_over_asthma': '''
            Professional Advice:
            - Low-calorie, anti-inflammatory diet
            - Light exercises with focus on breathing
            - Monitor respiratory status
            ''',
        'advice_obese_asthma': '''
            Professional Advice:
            - Diet under medical supervision
            - Low-impact exercises with supervision
            - Strict respiratory monitoring
            ''',
        'advice_under_arthritis': '''
            Professional Advice:
            - Omega-3 rich diet
            - Light flexibility exercises
            - Consult physiotherapist
            ''',
        'advice_normal_arthritis': '''
            Professional Advice:
            - Anti-inflammatory diet
            - Low-impact exercises like swimming
            - Regular joint monitoring
            ''',
        'advice_over_arthritis': '''
            Professional Advice:
            - Low-calorie, anti-inflammatory diet
            - Water-based and stretching exercises
            - Consult rheumatologist
            ''',
        'advice_obese_arthritis': '''
            Professional Advice:
            - Diet under medical supervision
            - Low-impact exercises with supervision
            - Weight loss to reduce joint stress
            ''',
        'advice_under_kidney_disease': '''
            Professional Advice:
            - Low-protein, low-salt diet
            - Light exercise under medical supervision
            - Monitor kidney function
            ''',
        'advice_normal_kidney_disease': '''
            Professional Advice:
            - Controlled kidney-friendly diet
            - Light aerobic exercises
            - Regular kidney checkups
            ''',
        'advice_over_kidney_disease': '''
            Professional Advice:
            - Low-protein, low-salt diet
            - Low-impact exercises
            - Strict kidney function monitoring
            ''',
        'advice_obese_kidney_disease': '''
            Professional Advice:
            - Diet under nephrologist supervision
            - Low-impact exercises with supervision
            - Monitor weight and kidney function
            ''',
        'advice_under_thyroid_disease': '''
            Professional Advice:
            - Iodine-rich diet (under medical supervision)
            - Light exercises for metabolism
            - Regular thyroid monitoring
            ''',
        'advice_normal_thyroid_disease': '''
            Professional Advice:
            - Balanced diet
            - Light aerobic and strength exercises
            - Regular thyroid checkups
            ''',
        'advice_over_thyroid_disease': '''
            Professional Advice:
            - Low-calorie diet
            - Light exercises for metabolism
            - Monitor thyroid hormones
            ''',
        'advice_obese_thyroid_disease': '''
            Professional Advice:
            - Diet under endocrinologist supervision
            - Low-impact exercises with supervision
            - Monitor weight and thyroid hormones
            ''',
        'plan_under_none': '''
            7-Day Plan:
            🥑 Breakfast: Spinach omelette + avocado
            🥜 Snack: Mixed nuts
            🍗 Lunch: Grilled chicken + brown rice
            🥛 Dinner: Lentil soup + whole grain bread
            ''',
        'plan_normal_none': '''
            7-Day Plan:
            🥚 Breakfast: Toast + veggie omelette
            🍎 Snack: Seasonal fruits
            🥩 Lunch: Beef steak + boiled potatoes
            🥦 Dinner: Protein salad + quinoa
            ''',
        'plan_over_none': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots & hummus
            🍤 Lunch: Grilled shrimp + steamed veggies
            🥟 Dinner: Chicken barley soup
            ''',
        'plan_obese_none': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + mushrooms
            🥑 Snack: Avocado with walnuts
            🥩 Lunch: Turkey breast + zucchini noodles
            🥬 Dinner: White fish + steamed broccoli
            ''',
        'plan_under_diabetes': '''
            7-Day Plan:
            🥚 Breakfast: Egg whites + veggies
            🥜 Snack: Raw almonds
            🍗 Lunch: Grilled chicken + green salad
            🥬 Dinner: Steamed fish + broccoli
            ''',
        'plan_normal_diabetes': '''
            7-Day Plan:
            🥗 Breakfast: Oats + berries
            🍎 Snack: Apple
            🍤 Lunch: Shrimp + steamed veggies
            🥦 Dinner: Chicken salad + quinoa
            ''',
        'plan_over_diabetes': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥕 Snack: Carrots
            🥩 Lunch: Grilled turkey + salad
            🥬 Dinner: White fish + veggies
            ''',
        'plan_obese_diabetes': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + spinach
            🥑 Snack: Avocado
            🍗 Lunch: Steamed chicken + zucchini
            🥬 Dinner: Fish + steamed veggies
            ''',
        'plan_under_hypertension': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + fruit
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_hypertension': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_hypertension': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-sodium veggie soup
            ''',
        'plan_obese_hypertension': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'plan_under_heart_disease': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + berries
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_heart_disease': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_heart_disease': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-fat veggie soup
            ''',
        'plan_obese_heart_disease': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'plan_under_asthma': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + berries
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_asthma': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_asthma': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-fat veggie soup
            ''',
        'plan_obese_asthma': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'plan_under_arthritis': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + berries
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_arthritis': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_arthritis': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-fat veggie soup
            ''',
        'plan_obese_arthritis': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'plan_under_kidney_disease': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + fruit
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_kidney_disease': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_kidney_disease': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-sodium veggie soup
            ''',
        'plan_obese_kidney_disease': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'plan_under_thyroid_disease': '''
            7-Day Plan:
            🥗 Breakfast: Low-fat yogurt + berries
            🍎 Snack: Apple
            🍗 Lunch: Grilled chicken + veggies
            🥬 Dinner: White fish + green salad
            ''',
        'plan_normal_thyroid_disease': '''
            7-Day Plan:
            🥚 Breakfast: Boiled egg + veggies
            🥜 Snack: Raw almonds
            🥩 Lunch: Lean beef + quinoa
            🥦 Dinner: Chicken salad + veggies
            ''',
        'plan_over_thyroid_disease': '''
            7-Day Plan:
            🥗 Breakfast: Green smoothie + oats
            🥕 Snack: Carrots
            🍤 Lunch: Steamed shrimp + veggies
            🥬 Dinner: Low-fat veggie soup
            ''',
        'plan_obese_thyroid_disease': '''
            7-Day Plan:
            🍳 Breakfast: Egg whites + veggies
            🥑 Snack: Avocado
            🍗 Lunch: Grilled turkey + zucchini
            🥬 Dinner: White fish + steamed veggies
            ''',
        'extra_tips': '''
            Universal Tips:
            ✅ 7-9 hours sleep
            ✅ 8 glasses of water daily
            ❌ Avoid processed foods
            ''',
        'exercise_under_none': '''
            🏋️ Exercise Routine:
            - Resistance training: 3 sets of 15 (light dumbbells)
            - Daily walking: 30 minutes
        ''',
        'exercise_normal_none': '''
            🏋️ Exercise Routine:
            - Crossfit: 4 sessions/week
            - Swimming: 2x/week
        ''',
        'exercise_over_none': '''
            🏋️ Exercise Routine:
            - Jogging: 45 mins 3x/week
            - Yoga: 2 sessions/week
        ''',
        'exercise_obese_none': '''
            🏋️ Exercise Routine:
            - HIIT: 5 sessions/week
            - Heavy weights with trainer
        ''',
        'exercise_under_diabetes': '''
            🏋️ Exercise Routine:
            - Light walking: 30 mins daily
            - Yoga: 2 sessions/week
        ''',
        'exercise_normal_diabetes': '''
            🏋️ Exercise Routine:
            - Cardio: 4 sessions/week
            - Stretching: 2 sessions/week
        ''',
        'exercise_over_diabetes': '''
            🏋️ Exercise Routine:
            - Brisk walking: 45 mins, 4x/week
            - Light resistance training: 2 sessions/week
        ''',
        'exercise_obese_diabetes': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 2 sessions/week
        ''',
        'exercise_under_hypertension': '''
            🏋️ Exercise Routine:
            - Light walking: 30 mins daily
            - Yoga: 3 sessions/week
        ''',
        'exercise_normal_hypertension': '''
            🏋️ Exercise Routine:
            - Cardio: 5 sessions/week
            - Stretching: 2 sessions/week
        ''',
        'exercise_over_hypertension': '''
            🏋️ Exercise Routine:
            - Brisk walking: 45 mins, 4x/week
            - Yoga: 2 sessions/week
        ''',
        'exercise_obese_hypertension': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 2 sessions/week
        ''',
        'exercise_under_heart_disease': '''
            🏋️ Exercise Routine:
            - Light walking: 20 mins daily
            - Stretching: 2 sessions/week
        ''',
        'exercise_normal_heart_disease': '''
            🏋️ Exercise Routine:
            - Light cardio: 4 sessions/week
            - Yoga: 2 sessions/week
        ''',
        'exercise_over_heart_disease': '''
            🏋️ Exercise Routine:
            - Brisk walking: 30 mins, 4x/week
            - Light resistance training: 2 sessions/week
        ''',
        'exercise_obese_heart_disease': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 2 sessions/week
        ''',
        'exercise_under_asthma': '''
            🏋️ Exercise Routine:
            - Breathing exercises: 15 mins daily
            - Light walking: 20 mins daily
        ''',
        'exercise_normal_asthma': '''
            🏋️ Exercise Routine:
            - Light cardio: 4 sessions/week
            - Breathing exercises: 3 sessions/week
        ''',
        'exercise_over_asthma': '''
            🏋️ Exercise Routine:
            - Brisk walking: 30 mins, 4x/week
            - Yoga with breathing focus: 2 sessions/week
        ''',
        'exercise_obese_asthma': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming with breathing control: 2 sessions/week
        ''',
        'exercise_under_arthritis': '''
            🏋️ Exercise Routine:
            - Flexibility exercises: 20 mins daily
            - Swimming: 2 sessions/week
        ''',
        'exercise_normal_arthritis': '''
            🏋️ Exercise Routine:
            - Water-based exercises: 4 sessions/week
            - Stretching: 3 sessions/week
        ''',
        'exercise_over_arthritis': '''
            🏋️ Exercise Routine:
            - Light walking: 30 mins, 4x/week
            - Water-based exercises: 2 sessions/week
        ''',
        'exercise_obese_arthritis': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 3 sessions/week
        ''',
        'exercise_under_kidney_disease': '''
            🏋️ Exercise Routine:
            - Light walking: 20 mins daily
            - Stretching: 2 sessions/week
        ''',
        'exercise_normal_kidney_disease': '''
            🏋️ Exercise Routine:
            - Light cardio: 4 sessions/week
            - Yoga: 2 sessions/week
        ''',
        'exercise_over_kidney_disease': '''
            🏋️ Exercise Routine:
            - Light walking: 30 mins, 4x/week
            - Light resistance training: 2 sessions/week
        ''',
        'exercise_obese_kidney_disease': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 2 sessions/week
        ''',
        'exercise_under_thyroid_disease': '''
            🏋️ Exercise Routine:
            - Light walking: 20 mins daily
            - Yoga: 2 sessions/week
        ''',
        'exercise_normal_thyroid_disease': '''
            🏋️ Exercise Routine:
            - Light cardio: 4 sessions/week
            - Light resistance training: 2 sessions/week
        ''',
        'exercise_over_thyroid_disease': '''
            🏋️ Exercise Routine:
            - Brisk walking: 30 mins, 4x/week
            - Yoga: 2 sessions/week
        ''',
        'exercise_obese_thyroid_disease': '''
            🏋️ Exercise Routine:
            - Low-impact exercises: 5 sessions/week
            - Swimming: 2 sessions/week
        ''',
        # --- بیماری‌های جدید و توصیه‌ها (EN) ---
        'condition_cholesterol': 'High Cholesterol',
        'condition_anemia': 'Anemia',
        'condition_depression': 'Depression',
        'condition_digestive_disorder': 'Digestive Disorder',
        'condition_osteoporosis': 'Osteoporosis',
        # Cholesterol
        'advice_normal_cholesterol': '''- Reduce saturated fats\n- Use olive oil and fish\n- Daily walking''',
        'plan_normal_cholesterol': '''- Breakfast: Oatmeal + walnuts\n- Lunch: Grilled fish + veggies\n- Dinner: Barley soup + green salad''',
        'exercise_normal_cholesterol': '''- Brisk walking: 30 min daily\n- Cycling: 2x/week''',
        'extra_tips_normal_cholesterol': '''- Avoid fried foods\n- High fiber intake''',
        'supplements_normal_cholesterol': '''- Omega 3\n- Soluble fiber''',
        'warnings_normal_cholesterol': '''- Avoid excess eggs and red meat\n- Regular cholesterol check''',
        # Anemia
        'advice_normal_anemia': '''- Eat iron-rich foods (red meat, lentils)\n- Take vitamin C with meals\n- Avoid tea after meals''',
        'plan_normal_anemia': '''- Breakfast: Egg + orange juice\n- Lunch: Lentil stew + meat\n- Dinner: Spinach soup''',
        'exercise_normal_anemia': '''- Light walking\n- Yoga''',
        'extra_tips_normal_anemia': '''- Regular blood tests\n- Iron supplements if needed''',
        'supplements_normal_anemia': '''- Iron\n- Vitamin C''',
        'warnings_normal_anemia': '''- Avoid dairy with iron\n- Consult your doctor''',
        # Depression
        'advice_normal_depression': '''- Omega-3 fatty acids\n- Regular exercise\n- Enough sleep''',
        'plan_normal_depression': '''- Breakfast: Whole grain bread + walnuts\n- Lunch: Salmon + veggies\n- Dinner: Barley soup''',
        'exercise_normal_depression': '''- Nature walks\n- Meditation and yoga''',
        'extra_tips_normal_depression': '''- Stay socially active\n- Avoid stress''',
        'supplements_normal_depression': '''- Omega 3\n- Vitamin D''',
        'warnings_normal_depression': '''- Avoid alcohol\n- Consult a psychiatrist''',
        # Digestive Disorder
        'advice_normal_digestive_disorder': '''- High fiber intake\n- Avoid fatty and fried foods\n- Small frequent meals''',
        'plan_normal_digestive_disorder': '''- Breakfast: Low-fat yogurt + fruit\n- Lunch: Brown rice + steamed veggies\n- Dinner: Veggie soup''',
        'exercise_normal_digestive_disorder': '''- Gentle walk after meals\n- Stretching''',
        'extra_tips_normal_digestive_disorder': '''- Drink enough water\n- Avoid overeating''',
        'supplements_normal_digestive_disorder': '''- Probiotics\n- Fiber''',
        'warnings_normal_digestive_disorder': '''- Avoid soda and fast food\n- Consult a gastroenterologist''',
        # Osteoporosis
        'advice_normal_osteoporosis': '''- Low-fat dairy\n- Get vitamin D and calcium\n- Weight-bearing exercise''',
        'plan_normal_osteoporosis': '''- Breakfast: Low-fat milk + whole grain bread\n- Lunch: Chicken + broccoli\n- Dinner: Milk soup''',
        'exercise_normal_osteoporosis': '''- Brisk walking\n- Resistance training''',
        'extra_tips_normal_osteoporosis': '''- Sun exposure\n- Avoid smoking''',
        'supplements_normal_osteoporosis': '''- Calcium\n- Vitamin D''',
        'warnings_normal_osteoporosis': '''- Avoid soda\n- Consult your doctor''',
        # افزودن مقدار پیش‌فرض برای مکمل‌ها و هشدارها (EN)
        'supplements_default': 'Take appropriate supplements after consulting your doctor.',
        'warnings_default': 'If you have a medical condition, consult your doctor.'
    }
}

# تابع محاسبه شاخص توده بدنی (BMI)
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100  # تبدیل سانتی‌متر به متر
    return round(weight / (height_m ** 2), 1)  # محاسبه BMI و گرد کردن به یک رقم اعشار

# تابع تعیین وضعیت BMI و تصویر متناسب با آن
def get_bmi_status(bmi):
    if bmi < 18.5:
        return 'status_under', 'underweight.png'  # کمبود وزن
    elif 18.5 <= bmi < 24.9:
        return 'status_normal', 'normal.png'  # وزن طبیعی
    elif 25 <= bmi < 29.9:
        return 'status_over', 'overweight.png'  # اضافه وزن
    else:
        return 'status_obese', 'obese.png'  # چاقی مفرط

# تابع محاسبه محدوده وزن نرمال بر اساس قد
def calculate_normal_weight_range(height_cm):
    height_m = height_cm / 100  # تبدیل سانتی‌متر به متر
    min_bmi = 18.5  # حداقل BMI برای وزن نرمال
    max_bmi = 24.9  # حداکثر BMI برای وزن نرمال
    min_weight = round(min_bmi * (height_m ** 2), 1)  # حداقل وزن نرمال
    max_weight = round(max_bmi * (height_m ** 2), 1)  # حداکثر وزن نرمال
    return min_weight, max_weight

@app.route('/', methods=['GET', 'POST'])
def index():
    lang = request.args.get('lang', 'fa')  # دریافت زبان (پیش‌فرض فارسی)
    tr = translations.get(lang, translations['fa'])  # دریافت ترجمه‌ها
    
    if request.method == 'POST':
        # دریافت اطلاعات فرم از کاربر
        full_name = request.form.get('full_name', '')  # نام کامل
        gender = request.form.get('gender', 'none')  # جنسیت
        age = int(request.form.get('age', 0))  # سن
        height = float(request.form.get('height', 0.0))  # قد
        height_unit = request.form.get('height_unit', 'cm')  # واحد قد
        weight = float(request.form.get('weight', 0.0))  # وزن
        weight_unit = request.form.get('weight_unit', 'kg')  # واحد وزن
        condition = request.form.get('condition', 'none')  # بیماری زمینه‌ای
        lang = request.form.get('lang', 'fa')  # زبان

        # تبدیل واحدها به متریک
        if height_unit == 'inch':
            height *= 2.54  # تبدیل اینچ به سانتی‌متر
        if weight_unit == 'lb':
            weight *= 0.453592  # تبدیل پوند به کیلوگرم

        # محاسبه BMI و وضعیت
        bmi = calculate_bmi(weight, height)  # محاسبه BMI
        reduced_bmi = calculate_bmi(weight - 10, height)  # محاسبه BMI برای وزن کاهش‌یافته
        status, status_image = get_bmi_status(bmi)  # تعیین وضعیت و تصویر
        min_weight, max_weight = calculate_normal_weight_range(height)  # محدوده وزن نرمال

        # مدیریت آپلود تصویر پروفایل
        avatar_path = f'static/images/{gender}.png'  # مسیر پیش‌فرض تصویر
        image = request.files.get('avatar')  # دریافت فایل تصویر
        if image and image.filename != '':
            filename = secure_filename(image.filename)  # امن‌سازی نام فایل
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # ذخیره فایل
            avatar_path = f'uploads/{filename}'  # مسیر جدید تصویر

        # نمایش نتایج به کاربر
        return render_template('result.html',
            full_name=full_name,
            age=age,
            gender=gender,
            height=round(height, 1),
            weight=round(weight, 1),
            bmi=bmi,
            reduced_bmi=reduced_bmi,
            status=status,
            condition=condition,
            avatar=avatar_path,
            status_image=status_image,
            lang=lang,
            tr=tr,
            min_weight=min_weight,
            max_weight=max_weight,
            theme_colors={  
                'primary': '#ADB2D4',  # رنگ اصلی
                'secondary': '#C7D9DD'  # رنگ ثانویه
            }
        )
    
    return render_template('index.html', lang=lang, tr=tr)  # نمایش فرم ورود اطلاعات

@app.route('/download/pdf')
def download_pdf():
    try:
        # دریافت پارامترها از URL
        lang = request.args.get('lang', 'fa')  # زبان
        full_name = request.args.get('full_name', '')  # نام کامل
        bmi = request.args.get('bmi', '')  # شاخص توده بدنی
        status = request.args.get('status', '')  # وضعیت
        age = request.args.get('age', '')  # سن
        height = request.args.get('height', '')  # قد
        weight = request.args.get('weight', '')  # وزن
        condition = request.args.get('condition', '')  # بیماری زمینه‌ای

        # تبدیل مقادیر رشته‌ای به عدد
        try:
            height_val = float(height)  # تبدیل قد به عدد
        except:
            height_val = 0
        try:
            weight_val = float(weight)  # تبدیل وزن به عدد
        except:
            weight_val = 0
        try:
            bmi_val = float(bmi)  # تبدیل BMI به عدد
        except:
            bmi_val = 0

        # محاسبه محدوده وزن نرمال
        min_weight, max_weight = calculate_normal_weight_range(height_val)  # محدوده وزن نرمال

        # تولید محتوای HTML برای PDF
        html_content = render_template('result.html',
                             lang=lang,
                             full_name=full_name,
                             bmi=bmi_val,
                             status=status,
                             age=age,
                             height=height_val,
                             weight=weight_val,
                             condition=condition,
                             tr=translations[lang],
                             avatar='images/default_avatar.png',
                             status_image='status_normal.png',
                             min_weight=min_weight,
                             max_weight=max_weight,
                             is_pdf=True)  # حالت PDF

        # تنظیمات pdfkit برای تولید PDF
        options = {
            'page-size': 'A4',  # اندازه صفحه
            'margin-top': '0.75in',  # حاشیه بالا
            'margin-right': '0.75in',  # حاشیه راست
            'margin-bottom': '0.75in',  # حاشیه پایین
            'margin-left': '0.75in',  # حاشیه چپ
            'encoding': 'UTF-8',  # کدگذاری
            'no-outline': None,  # بدون فهرست
            'enable-local-file-access': None,  # دسترسی به فایل‌های محلی
            'quiet': '',  # بدون پیام
            'print-media-type': '',  # نوع رسانه چاپ
            'dpi': 300,  # وضوح تصویر
            'image-quality': 100,  # کیفیت تصویر
            'enable-smart-shrinking': '',  # کاهش هوشمند
            'disable-smart-shrinking': '',  # غیرفعال کردن کاهش هوشمند
            'zoom': 1.0,  # بزرگنمایی
            'custom-header': [
                ('Accept-Encoding', 'gzip')  # هدر سفارشی
            ],
            'no-stop-slow-scripts': '',  # توقف اسکریپت‌های کند
            'debug-javascript': '',  # اشکال‌زدایی جاوااسکریپت
            'load-error-handling': 'ignore',  # مدیریت خطای بارگذاری
            'load-media-error-handling': 'ignore'  # مدیریت خطای رسانه
        }

        # تولید PDF و ارسال به کاربر
        config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')  # مسیر برنامه wkhtmltopdf
        pdf = pdfkit.from_string(html_content, False, options=options, configuration=config)  # تولید PDF از HTML
        pdf_io = io.BytesIO(pdf)  # تبدیل به بافر باینری
        pdf_io.seek(0)  # بازگشت به ابتدای بافر
        return send_file(
            pdf_io,
            mimetype='application/pdf',  # نوع فایل PDF
            as_attachment=True,  # دانلود به صورت فایل پیوست
            download_name=f'BMI_Result_{full_name}.pdf'  # نام فایل خروجی
        )
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")  # ثبت خطا در لاگ
        return f"Error generating PDF: {str(e)}", 500  # پیام خطا به کاربر

from selenium.common.exceptions import TimeoutException

@app.route('/download/image')
def download_image():
    try:
        # دریافت پارامترها از URL
        lang = request.args.get('lang', 'fa')  # زبان
        full_name = request.args.get('full_name', '')  # نام کامل
        bmi = request.args.get('bmi', '')  # شاخص توده بدنی
        status = request.args.get('status', '')  # وضعیت
        age = request.args.get('age', '')  # سن
        height = request.args.get('height', '')  # قد
        weight = request.args.get('weight', '')  # وزن
        condition = request.args.get('condition', '')  # بیماری زمینه‌ای
        avatar = request.args.get('avatar', 'static/images/none.png')  # تصویر پروفایل
        if not avatar or avatar == '':
            avatar = 'static/images/none.png'  # تصویر پیش‌فرض

        # تبدیل مقادیر رشته‌ای به عدد
        try:
            height_val = float(height)  # تبدیل قد به عدد
        except:
            height_val = 0
        try:
            weight_val = float(weight)  # تبدیل وزن به عدد
        except:
            weight_val = 0
        try:
            bmi_val = float(bmi)  # تبدیل BMI به عدد
        except:
            bmi_val = 0

        # محاسبه محدوده وزن نرمال
        min_weight, max_weight = calculate_normal_weight_range(height_val)  # محدوده وزن نرمال

        # تولید محتوای HTML برای تصویر
        html = render_template('result.html',
                             lang=lang,
                             full_name=full_name,
                             bmi=bmi_val,
                             status=status,
                             age=age,
                             height=height_val,
                             weight=weight_val,
                             condition=condition,
                             tr=translations[lang],
                             avatar=avatar,
                             status_image='status_normal.png',
                             min_weight=min_weight,
                             max_weight=max_weight,
                             is_pdf=True)  # حالت تصویر

        # تنظیمات مرورگر کروم برای گرفتن اسکرین‌شات
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # اجرا بدون رابط گرافیکی
        chrome_options.add_argument('--no-sandbox')  # غیرفعال کردن sandbox
        chrome_options.add_argument('--disable-dev-shm-usage')  # غیرفعال کردن shared memory
        chrome_options.add_argument('--disable-gpu')  # غیرفعال کردن GPU
        chrome_options.add_argument('--window-size=1920,1080')  # اندازه پنجره
        chrome_options.add_argument('--force-device-scale-factor=1')  # مقیاس دستگاه

        # ایجاد درایور کروم
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        try:
            # بارگذاری HTML در مرورگر
            driver.get('data:text/html;charset=utf-8,' + html)  # بارگذاری محتوای HTML

            # انتظار برای بارگذاری کامل صفحه
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))  # اطمینان از بارگذاری body
            )

            # تنظیم اندازه پنجره مرورگر
            driver.set_window_size(1920, 1080)  # اندازه پنجره

            # گرفتن اسکرین‌شات از صفحه
            screenshot = driver.get_screenshot_as_png()  # دریافت اسکرین‌شات
            screenshot_io = io.BytesIO(screenshot)  # تبدیل به بافر باینری
            screenshot_io.seek(0)  # بازگشت به ابتدای بافر

            # ذخیره تصویر به فرمت JPEG
            img = Image.open(screenshot_io)  # باز کردن تصویر
            img = img.convert('RGB')  # تبدیل به RGB
            output = io.BytesIO()  # بافر خروجی
            img.save(output, format='JPEG', quality=95)  # ذخیره به صورت JPEG
            output.seek(0)  # بازگشت به ابتدای بافر

            # ارسال تصویر به کاربر
            return send_file(
                output,
                mimetype='image/jpeg',  # نوع فایل تصویر
                as_attachment=True,  # دانلود به صورت فایل پیوست
                download_name=f'BMI_Result_{full_name}.jpg'  # نام فایل خروجی
            )

        finally:
            driver.quit()  # بستن مرورگر

    except Exception as e:
        app.logger.error(f"Image generation error: {str(e)}")  # ثبت خطا در لاگ
        return f"Error generating image: {str(e)}", 500  # پیام خطا به کاربر

@app.route('/result-page')
def result_page():
    return render_template('result.html',
        full_name=request.args.get('full_name'),
        age=request.args.get('age'),
        gender=request.args.get('gender'),
        height=request.args.get('height'),
        weight=request.args.get('weight'),
        bmi=request.args.get('bmi'),
        min_weight=request.args.get('min_weight'),
        max_weight=request.args.get('max_weight'),
        status=request.args.get('status'),
        condition=request.args.get('condition', 'none'),
        avatar=request.args.get('avatar', 'static/images/none.png'),
        status_image=request.args.get('status_image', 'normal.png'),
        lang=request.args.get('lang', 'fa'),
        tr=translations.get(request.args.get('lang', 'fa'), translations['fa'])
    )

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)