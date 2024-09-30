import os
from datetime import datetime

# Try importing external libraries
try:
    import customtkinter
    import yagmail
    from fpdf import FPDF
    import matplotlib
# Try installing modules automatically if there are not installed
except ModuleNotFoundError and ImportError:
    try:
        os.system("install_modules.bat")
    # Advise user to manually download modules if the download fails
    except:
        raise Exception("""APPLICATION STOPPED: Modules were unable to be downloaded automatically.
Please check the README for manual download options.""")

import frontend
import backend
import crud_functionality as crud

if __name__ == "__main__":
    _, date_created = backend.get_recent_backup("ecommerce")
    # If backup has not been created for the day
    if date_created != datetime.now().strftime("%d-%m-%y"):
        backend.backup("ecommerce")
    # Create placeholder image if it doesn't yet exist
    backend.create_placeholder()
    # Configure encryption
    admin_account = crud.search_table("ecommerce", "Staff", "*", "staff_id = '1'")[0]
    if backend.get_should_encrypt() and admin_account.get("username")[0] == "|":
        backend.encrypt_all()
    elif not backend.get_should_encrypt() and admin_account.get("username")[0] == "^":
        backend.decrypt_all()
    # Create application and display
    application = frontend.RootWindow()
    application.mainloop()
