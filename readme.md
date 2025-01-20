# Social Network Analyser

The program provides you to get statistical data on the number of views, 
likes, reposts, comments under the posts of three social networks: 
vk.ru, ok.ru and telegram. Data is collected for a period of time 
(by default - for the past week) and consolidated into a single excel file. 
The maximum and minimum values ​​are highlighted in green and red, respectively.


# Example:
main.py


# Dependencies:
requirements.txt

pip install openpyxl

pip install python-dotenv

pip install ok-api

pip install Telethon


# Settings pattern:
settings_pattern.txt

Fill the pattern identificators with your personal API tokens and other credential information. 
Rename settings_pattern.txt to settings.txt