# Export Data from MyDataHelps API

## Setup

To access the MyDataHelps API for the Glow Up project, you need an account with MDH Designer:
1. Register an account at https://designer.mydatahelps.org/
2. Ping Magdalena Fuchs on Discord or Email at magdalena.fuch@mtec.ethz.ch providing the email with which you registered to MDH
3. Create a private RSA key for the service account `MyDataHelps.D2F2C4E0.glowup_service` by following these steps:

    - In MDH Designer, navigate to ``Settings > Workspace Settings > Service Accounts` (see provided screenshots) 
    
    ![Step 1](img/rsa_instructions_1.png) 

    ![Step 2](img/rsa_instructions_2.png)

    - Select `Add New Key > Add Key` (leave the optional field blank) ![Step 3](img/rsa_instructions_3.png)
    - Copy the private key (`-----BEGIN RSA PRIVATE KEY----- [...] -----END RSA PRIVATE KEY-----`) ![Step 4](img/rsa_instructions_4.png)
    - In this current folder, create a file called `rks_private_key.pem` and paste the full private key into it. Save and close. Do not share this key or upload it.
4. Install all needed python packages: Run `pip3 install -r requirements.txt` in your terminal

##  Export

Run `export_participant_data.ipyn` with your selected input. Read through the instruction steps in the Jupyer Notebook.

## Code Structure

- `./.env` contains global environment variables (e.g., service account ID, path to private access key)
- `./api_utils.py` contains helper code for interacting with the MDH API
- `./export_paticipant_data.ipynb` main file to execute for generating .csv files from participant data
- `./apple_health.py` & `./health_connect.py` contain code to access either AppleHealth or HealthConnect data, they translate common names for measures to the specific data type in the corresponding namespace (e.g., "exercise_time" -> "AppleExerciseTime"). These two files are almost identical at the moment but kept separately in case we need to extend functionality later on (as HC and AH data structures are returned differently). We may thinkg about a class/adapter structure in the future. 

### Adding to the project

If you add code to the project or edit anything, please use a separate Git branch, write a clear and coherent commit message, and clear all Jupyter notebook outputs before committing.