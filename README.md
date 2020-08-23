[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# Lancer Attendance

This attendance system modernized the manual attendance system that predated it. It was built using Flask and Google Sheets coupled with the MFRC522 library to provide an automatic solutions to taking attendance. When creating the system, I settled upon using something that everyone carried around, their student ID card. I combined the RFID reader with a Raspberry PI in kiosk mode to allow a seamless experience. I chose Flask as it was the simplest route to run a webserver and also allow interaction with UI.

## Table of ContentI'm
* [Installation](#install) 
* [Hardware](#hardware)
* [License](#license)

## <div id="install"> Installation </div>
1. Install flask, gspread, and oauth2 using pip
2. Create Google Sheets to store the data
3. Update attendance.py with the sheet's name
4. Run the app


## <div id="hardware"> Hardware </div>
- Raspberry PI
- MFRC522 RFID Reader

## <div id="software"> Software </div>
- Flask
- MFRC522 Library
- Gspread

##  <div id="license">  License </div>

  + [MIT](https://choosealicense.com/licenses/mit/)
