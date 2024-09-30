Welcome to the Turtle Tennis documentation!



(i) Specifications

Operating system: Windows
Python version: 3.8+
IDEs used: Python's IDLE (v3.8) and PyCharm (v2022.3.1)

(ii) Imports Needed

The application will detect any external libraries and attempt to download them automatically upon starting.

If automatic download fails, the libraries can be installed manually instead:
	customtkinter v5.0.3+ (https://pypi.org/project/customtkinter/): type "pip install customtkinter" into your system terminal
	fpdf2 v2.6.1+ (https://pypi.org/project/Pillow/): type "pip install pillow" into your system terminal
	yagmail v0.15.293+ (https://pypi.org/project/yagmail/): type "pip install yagmail" into your system terminal
	matplotlib v3.7.0+ (https://pypi.org/project/matplotlib/): type "pip install matplotlib" into your system terminal

(iii) Starting the application

The application should be started by running the python file titled "app.py".

(iv) Logging in

A user may log in by creating an account and logging in with that new account. Alternatively, sample accounts of different access levels are 
detailed below:
	
	Customer
		Username: jcurrie123
		Password: HiThere123

	Management staff
		Username: management
		Password: Tt123
	
	Sales staff
		Username: sales
		Password: Tt123

(v) Validation

Validation is employed for all entry widgets except for those whose purpose is:
	- to enter search criteria 
	- to enter login details 
To make moderation and testing easier, entry widgets will highlight red if the input is invalid and will detail how it is invalid.

(vi) Images

All images used automatically in the application's UI are located in the 'images' directory.

When creating or updating products, the application will prompt the user for an image. Images can be located in any directory but must be a .png or .jpg file.



Have fun shopping!
From the Turtle Tennis Team.
