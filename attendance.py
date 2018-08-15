import os
import time

from flask import Flask, render_template, redirect, url_for, request, send_from_directory

import RPi.GPIO as GPIO
import MFRC522
import datetime
import gspread
from gspread import CellNotFound
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
MIFAREReader = MFRC522.MFRC522()
has_id = False

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('/home/pi/LancerAttendanceSheet.json', scope)

gc = gspread.authorize(credentials)

worksheet = gc.open("LancerAttendance").sheet1


def next_available_row(ws):
    str_list = list(filter(None, ws.col_values(3)))
    return str(len(str_list)+1)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/signIn")
def sign_in():
    gc.login()
    start_time = time.time()

    while not has_id:
        if time.time() - start_time > 5:
            return redirect(url_for('index'))

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

                data_cell = None
                try:
                    data_cell = worksheet.find(uid_string)
                except CellNotFound:
                    pass

                current_date = datetime.datetime.now().strftime('%m/%d').lstrip("0").replace(" 0", " ")

                date_cell = None

                try:
                    date_cell = worksheet.find(current_date)
                except CellNotFound:
                    pass

                current_time = datetime.datetime.now().strftime('%I:%M %p')

                if date_cell is not None:
                    first_name = ''

                    if data_cell is None:
                        row = next_available_row(worksheet)
                        worksheet.update_acell("C{}".format(row), uid_string)
                        worksheet.update_cell(row, date_cell.col, current_time)
                    else:
                        first_name = worksheet.cell(data_cell.row, 1).value
                        worksheet.update_cell(data_cell.row, date_cell.col, current_time)

                    return render_template('sign.html', message='Welcome to robotics', name=first_name)
                else:
                    return render_template('sign.html', message='Error. Date not set in spreadsheet', name='')


@app.route("/signOut")
def sign_out():
    gc.login()
    start_time = time.time()

    while not has_id:
        if time.time() - start_time > 5:
            return redirect(url_for('index'))

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

                data_cell = None
                try:
                    data_cell = worksheet.find(uid_string)
                except CellNotFound:
                    pass

                current_date = datetime.datetime.now().strftime('%m/%d').lstrip("0").replace(" 0", " ")

                date_cell = None

                try:
                    date_cell = worksheet.find(current_date)
                except CellNotFound:
                    pass

                current_time = datetime.datetime.now().strftime('%I:%M %p')

                if date_cell is not None:
                    first_name = ''

                    if data_cell is None:
                        row = next_available_row(worksheet)
                        worksheet.update_acell("C{}".format(row), uid_string)
                        worksheet.update_cell(row, date_cell.col, current_time)
                    else:
                        first_name = worksheet.cell(data_cell.row, 1).value
                        worksheet.update_cell(data_cell.row, date_cell.col + 1, current_time)

                    return render_template('sign.html', message='Have a nice day', name=first_name)
                else:
                    return render_template('sign.html', message='Error. Date not set in spreadsheet! :(', name='')


@app.route("/signUp", methods=['POST', 'GET'])
def sign_up():
    gc.login()

    if request.method == 'POST':
        rfid_number = int(request.form['rfidNumber'])
        first_name = str(request.form['firstName'])
        last_name = str(request.form['lastName'])

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

    while not has_id:
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
