import os
import time

from flask import Flask, render_template, redirect, url_for, request, send_from_directory

import RPi.GPIO as GPIO
import MFRC522
import datetime
import gspread
from gspread import CellNotFound
from oauth2client.service_account import ServiceAccountCredentials

import socket

# Hang if we have no internet connection
while True:
    try:
        host = socket.gethostbyname('www.google.com')
        s = socket.create_connection((host, 80), 2)
        break
    except:
        pass


app = Flask(__name__)
MIFAREReader = MFRC522.MFRC522()

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/LancerAttendanceSheet.json', scope)

gc = gspread.authorize(credentials)

worksheet = gc.open("LancerAttendance").sheet1

current_date = datetime.datetime.now().strftime('%m/%d').lstrip("0").replace("0", "")

date_cell = None
rfid_col = 3

try:
    date_cell = worksheet.find(current_date)
except CellNotFound:
    current_date = None


def next_available_row(ws):
    str_list = list(filter(None, ws.col_values(rfid_col)))
    return str(len(str_list)+1)


def get_current_date():
    global current_date, date_cell
    newest_date = datetime.datetime.now().strftime('%m/%d').lstrip("0").replace("0", "")

    if newest_date != current_date:
        current_date = newest_date
        
        try:
            date_cell = worksheet.find(current_date)
        except CellNotFound:
            current_date = None


def scan_rfid():
    uid_string = ''
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:

        # Get the UID of the card
        (status, uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            for uid_part in uid:
                uid_string += str(uid_part)

    return uid_string


def handle_signing(is_signing_in):
    
    gc.login()
    get_current_date()

    if date_cell is None:
        return render_template('error.html', error='Error. Date not set in spreadsheet. Please contact Johnson')
    
    start_time = time.time()
    
    while True:
        if time.time() - start_time > 5:
            return redirect(url_for('index'))

        uid_string = scan_rfid()

        if uid_string != '':
            try:
                data_cell = worksheet.find(uid_string)
            except CellNotFound:
                return render_template('error.html', error='Who are you? You are not registered!')

            current_time = datetime.datetime.now().strftime('%I:%M %p')

            first_name = worksheet.cell(data_cell.row, 1).value

            if is_signing_in:
                worksheet.update_cell(data_cell.row, date_cell.col, current_time)
                return render_template('signin.html', name=first_name)
            else:

                sign_in_time_cell = worksheet.cell(data_cell.row, date_cell.col)

                if sign_in_time_cell is not None:
                    sign_in_time_string = sign_in_time_cell.value
                    sign_in_time = datetime.datetime.strptime(sign_in_time_string, '%I:%M %p')

                    if (sign_in_time + datetime.timedelta(hours=2)).time() < datetime.datetime.now().time():
                        worksheet.update_cell(data_cell.row, date_cell.col + 1, current_time)
                        return render_template('signout.html', name=first_name)
                    else:
                        return render_template('error.html', error='You have to stay at least 2 hours to sign out. Talk to Rickey if you don\'t like that')
                else:
                    worksheet.update_cell(data_cell.row, date_cell.col + 1, current_time)
                    return render_template('signout.html', name=first_name)


@app.route("/")
def index():
    get_current_date()
    return render_template('index.html')


@app.route("/signIn")
def sign_in():
    return handle_signing(True)


@app.route("/signOut")
def sign_out():
    return handle_signing(False)


@app.route("/signUp", methods=['POST', 'GET'])
def sign_up():
    gc.login()

    if request.method == 'POST':
        rfid_number = int(request.form['rfidNumber'])
        first_name = str(request.form['firstName'])
        last_name = str(request.form['lastName'])

        rfid_values = worksheet.col_values(rfid_col)

        if str(rfid_number) in rfid_values:
            return render_template('error.html', error='You already sign up')

        row = next_available_row(worksheet)
        worksheet.update_acell("A{}".format(row), first_name)
        worksheet.update_acell("B{}".format(row), last_name)
        worksheet.update_acell("C{}".format(row), str(rfid_number))

        return render_template('signup.html', wasSignedUp=True, firstName=first_name)
    elif request.method == 'GET':
        uid = request.args.get('uid')

        if uid is not None:
            return render_template('signup.html', wasSignUp=False, rfidNumber=uid)

        return render_template('signup.html', wasSignedUp=False)


@app.route("/getRFID", methods=['GET'])
def get_rfid():
    start_time = time.time()

    while True:
        if time.time() - start_time > 5:
            return redirect(url_for('sign_up'))

        uid_string = ''
        # Scan for cards
        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # If a card is found
        if status == MIFAREReader.MI_OK:

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                for uid_part in uid:
                    uid_string += str(uid_part)

                return redirect(url_for('sign_up', uid=uid_string))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    try:
        app.run()
    except Exception as ex:
        pass
    finally:
        GPIO.cleanup()
