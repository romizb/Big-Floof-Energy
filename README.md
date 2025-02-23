# 🌟🐾 Big Floof Energy 🐾🌟  
### **The Ultimate Dog Care Manager for Roommates**  
![Jsmine Banner](https://github.com/romizb/Big-Floof-Energy/blob/main/jasmine%20banner.jpg)

<sub>_*🖥️✨ **A next-gen Flask web app that keeps your pup’s care on lock—because only the most elite floofs deserve VIP treatment!** 🐕💿🔥*_</sub>

---

## 🚀 About Big Floof Energy  

Big Floof Energy (BFE) is a **task manager designed for roommates** to easily **track and coordinate dog care duties**. From **daily walks and feedings** to **custom tasks** and **web scraping**, the app ensures everyone stays accountable while keeping your furry friend happy.  


---

## 🎀 How It Works  

1. **Start the App**  
   - Enter BFE\login via https://big-floof-energy-production-6650.up.railway.app/login


2. **Log In**  
   - Only predefined users can access the program (defined in app.py: "def add_predefined_users()").  
   - Usernames are case-insensitive for convenience.
   - For outside users, input the username "**stranger**" :).
   - Implementing a username-based-access helps the program assign task completion to spesific users, as well as increasing privacy of the app.
    

3. **Manage Tasks**  
   - See a **daily calendar** with preloaded dog care tasks.  
   - Tasks are grouped into:  
     - 🐕 **Walks** (morning, afternoon, evening, bedtime)  
     - 🍖 **Feedings** (twice daily)  
     - ✍️ **Custom Tasks** (user-added)  
   - Click to **mark/unmark tasks as complete**.  
   - **Leave notes** on completed tasks.
   - for increased visual convenience, previous dates that have all tasks complete are hidden from the user, whilst their data is kept in the system.

4. **View & Export Data**  
   - Tasks are logged with **timestamps & usernames**.  
   - Export **task records as a CSV file** for tracking.
   - All tasks, including thoes checked from previous days, are presented in the CSV file.

5. **Stay Updated on Dog News & Deals**  
   - A **web scraper** that fetches funny latest dog-related news.   

---

## 🖥️ Testing the program 

### 🛠️ Testing functionalities 
  - Ensures users and tasks are correctly stored and retrieved.
  - Verifies task completion toggling.
  - Confirms login works only for predefined users.
  - Checks if tasks are created daily.
  - Validates adding custom tasks.
  - Ensures it returns valid dog news data.

### 📌 Requirements  
Make sure you have:  
- **Python** (3.x recommended)  
- **Flask** (`pip install flask`)  
- **All requirements** (`pip install requirements.txt`)  
- **SQLite** (comes with Python)

### ▶️ Testing the BFE code  
1. Download (or "pull" via Git Bash) all files in the Big-Floof-Energy repository to your computer.
2. In the terminal, open a virtual environment (I use VSCode in WINDOWS, therefor these sample codes are fitted for such synthax):
```bash
env\Scripts\activate
```
3. Since app.py and scraper.py rely on environment variables to connect to the database, you need to temporarily override DATABASE_URL only while running tests:
```bash (WINDOWS)
$env:DATABASE_URL="sqlite:///:memory:"
```
4. Now test the program:
```bash
python -m unittest test_app.py
```
5. In your teminal you should get something like this:

![](https://github.com/romizb/Big-Floof-Energy/blob/main/old%20test%20result.png)

The “OK” at the end means all tests ran successfully and the functions in the Big-floof-energy are successfully running, bug free.


---
### 🌟 Lil' Bonus Perks 🌟  

- BFE is designed with mobile users in mind, so you can keep your floofies schedule tight from anywhere.  
- News scraping runs every 6 hours to incease the program's loading speed.  
- Keep your eyes peeled for some **top-secret** doggy Easter eggs... 🐶🦴🐔💿 Can you find them all? 👀✨


---
## Future Enhancements  
The work doesn’t stop here! Planned future improvements include:  

- **Enhancing the dog-friendly experience** with more visuals, interactive elements, and hidden Easter eggs.  
- **Multilingual support**, starting with Hebrew, to make the app accessible to a broader user base.  
- **Strengthening security** by encrypting sensitive keys within the code and integrating additional protective measures such as DDoS prevention and Firebase authentication.
- **Ongoing Debugging:** BFE is currently under active development, with a known issue causing the daily task generator to duplicate entries. A fix is in progress and is expected to be implemented within the next few days :)

Stay tuned for updates! 📡✨

---
*This program was written during my MS.c program in [Weizmann Institute](https://www.weizmann.ac.il/pages/), as part of a [python course](https://github.com/szabgab/wis-python-course-2024-11), tought by [Gabor Sabo](https://szabgab.com/) and toutered by [Liron Hoffman](https://liroh99.github.io/) and [Hadar Klimovski](https://hadarklimovski.github.io/).*

