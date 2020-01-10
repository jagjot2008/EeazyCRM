# EeazyCRM

#### Python based open source CRM developed using Flask framework

##### It's still WORK IN PROGRESS (I'm still building the modules)
##### But I have a small DEMO image below
![alt text](https://i.ibb.co/BsWm9Kf/eeazycrm-demo1.gif)

Features List
============

EeazyCRM contains the following modules (along with the 
completion progress report):

   1. Leads (99% complete)
   2. Accounts (90% complete)
   3. Contacts (99% complete)
   4. Deals (with Pipeline view) (90% complete)
   5. Activities (still building) (Not started as yet)
   6. Reports (with charts and graph) - (60% complete)
   7. Settings (50% complete)
       1. Roles Management (100% complete)
       2. User Management (100% complete)
       3. Profile Management (100% complete)
       4. Company Management (Not started)
       5. Configuration Management (Not started)
            1. Deal Stage
            2. Lead Stage
            3. Lead Source
            4. Activity Types
            5. Email Templates
       6. Application Settings (100% complete)
   8. Invoice (Not started)
   9. Dashboard (10% complete)
   
Depending upon the demand of this application, I'm also planning the
following:

   * Integration with WordPress Contact Form 7 (Lead Capture).
   * Integration with Google Contacts.
   * Integration with DropBox or Google Drive for Automatic Backups.
   * Integration with Email Service such as MailChimp.
   
Installation Requirements
============

1. Python3
2. Postgresql (ver 11+ or greater)
2. pip3
3. virtualenv

Make sure that the postgresql instance is up and running.

Open the command prompt or terminal and 
create a new database with the following commands.
    .. code-block:: python
    
        psql
        create database eeazy_crm

Installation Steps
============

1. Create a virtual environment using the following commands
    .. code-block:: python
    
        virtualenv -p python3 eeazycrm
        source eeazycrm/bin/activate
        
2. Add github repository using the following command

    .. code-block:: python
    
        cd eeazycrm
        git remote add origin https://github.com/jagjot2008/EeazyCRM
        git pull origin master
        
3. Now create the configuration file using the command
    .. code-block:: python
    
        cp config_vars.example config_vars.py
        
    Open the config_vars.py file and add the database connection 
    parameters in the PRODUCTION DATABASE SETTINGS (Default). 
    
    You can also setup the development and testing settings if you wish to.
        
3. Install the dependencies
   .. code-block:: python

       pip3 install -r requirements.txt

4. Create the following environment variables
   .. code-block:: python
   
       EMAIL_USER = <your username>
       EMAIL_PASS = <your password>
       
   If you want to run flask in development or testing mode set
   the following environment variable in addition to the above.
   .. code-block:: python
   
       FLASK_ENV = development, or
       FLASK_ENV = testing
   
5. Run the command
   .. code-block:: python
   
       python3 run.py
       
   This will run the installation wizard. Follow the instructions
   in the wizard and after finishing installation, stop the 
   application and start again by running the command in step #6.
   
That's it folks. Your CRM is running.

Report a Bug or Request a New Feature
================================

For reporting bugs in the system, you can raise a github issue or even request
a new feature.



