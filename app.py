from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime, time
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)
app.secret_key = "eduassist_secret_key"
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500"]
    )

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Morax@075",
    database="scheduler"
)

cursor = db.cursor(dictionary=True)
def fetch_sbtet_result(pin, semester):

    options = webdriver.EdgeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    driver = webdriver.Edge(
        service=Service(r"C:\WebDriver\msedgedriver.exe"),
        options=options
    )

    wait = WebDriverWait(driver, 10)

    try:

        driver.get(
            "https://sbtet.ap.gov.in/APSBTET/gradeWiseResults.do"
        )

        # Enter PIN
        pin_box = wait.until(
            EC.presence_of_element_located(
                (By.NAME, "aadhar1")
            )
        )

        pin_box.clear()
        pin_box.send_keys(pin)

        # Semester format conversion
        sem_text = f"{semester}SEM"

        # Select semester
        semester_dropdown = Select(
            driver.find_element(
                By.NAME,
                "grade2"
            )
        )

        semester_dropdown.select_by_visible_text(
            sem_text
        )

        # Submit
        driver.find_element(
            By.CSS_SELECTOR,
            ".btn.btn-primary"
        ).click()

        time.sleep(3)

        page_text = driver.page_source.upper()

        if (
            "NOT REGISTERED" in page_text
            or "REGISTERED BUT NOT ELIGIBLE" in page_text
            or "NO RECORDS" in page_text
        ):

            return {
                "success": False,
                "error": "No results found."
            }

        try:
            name = driver.find_element(
                By.XPATH,
                "//th[normalize-space()='Name']/following-sibling::td"
            ).text.strip()
        except:
            name = ""

        try:
            grand_total = driver.find_element(
                By.XPATH,
                "//th[normalize-space()='Grand Total']/following-sibling::td"
            ).text.strip()
        except:
            grand_total = ""

        try:
            gpa = driver.find_element(
                By.XPATH,
                "//th[normalize-space()='GPA']/following-sibling::td"
            ).text.strip()
        except:
            gpa = ""
        try:
            branch = driver.find_element(
                By.XPATH,
                "//th[normalize-space()='Branch Name']/following-sibling::td"
            ).text.strip()
        except:
            branch = ""
        try:
            result_status = driver.find_element(
                By.XPATH,
                "//th[normalize-space()='Result']/following-sibling::td"
            ).text.strip()
        except:
            result_status = ""

        cursor.execute("""
            INSERT INTO sbtet_results
            (
                pin,
                semester,
                student_name,
                grand_total,
                gpa,
                result_status
            )
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            pin,
            semester,
            name,
            grand_total,
            gpa,
            result_status
        ))

        db.commit()
        print(branch)
        return {
            "success": True,
            "name": name,
            "branch": branch,
            "grand_total": grand_total,
            "gpa": gpa,
            "result": result_status
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

    finally:
        driver.quit()
def get_next_class(semester):

    periods = {
        1: (time(9,30), time(10,20)),
        2: (time(10,20), time(11,10)),
        3: (time(11,20), time(12,10)),
        4: (time(12,10), time(13,0)),
        5: (time(13,40), time(14,30)),
        6: (time(14,30), time(15,20)),
        7: (time(15,20), time(16,10))
    }

    current_time = datetime.now().time()
    today = datetime.now().strftime("%A")

    next_period = None

    for period, (start, end) in periods.items():

        if current_time < start:
            next_period = period
            break

    if not next_period:
        return "No more classes for today "

    cursor.execute("""
        SELECT subject
        FROM timetable
        WHERE semester=%s
        AND day_name=%s
        AND period_no=%s
    """,(semester, today, str(next_period)))

    result = cursor.fetchone()

    if result:
        return f"{result['subject']} (P{next_period})"

    return "No class found"
def get_performance(pin):

    cursor.execute("""
        SELECT subject, final_avg
        FROM marks
        WHERE pin=%s
    """,(pin,))

    results = cursor.fetchall()

    if not results:
        return {
            "performance":"No Data",
            "weak_subject":"N/A",
            "overall":0
        }

    total = 0
    lowest_marks = 999
    weak_subject = "N/A"

    for row in results:

        total += row['final_avg']

        if row['final_avg'] < lowest_marks:

            lowest_marks = row['final_avg']
            weak_subject = row['subject']

    overall = round(total / len(results),2)

    if overall >= 35:
        performance = "Excellent"

    elif overall >= 28:
        performance = "Good"

    else:
        performance = "Average"

    return {
        "performance":performance,
        "weak_subject":weak_subject,
        "overall":overall
    }


@app.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    pin = data.get("pin")
    password = data.get("password")


    cursor.execute(
        """
        SELECT pin,name
        FROM student_data
        WHERE pin=%s
        AND password=%s
        """,
        (pin, password)
    )

    student = cursor.fetchone()


    if student:

        session['pin'] = student['pin']
        session['name'] = student['name']


        return jsonify({
            "success": True,
            "message": "Login successful"
        })


    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })

@app.route('/profile',methods=['GET'])
def profile():
    if 'pin' not in session:
        return jsonify({
            "success":False
        })
    cursor.execute("""
                   SELECT name,pin,branch,attendance 
                   FROM student_data
                   WHERE pin=%s
                   """,(session['pin'],))
    student = cursor.fetchone()
    return jsonify({
        "success":True,
        "name":student['name'],
        "pin":student['pin'],
        "branch":student['branch'],
        "attendance":student['attendance']
    })
@app.route("/notifications", methods=["GET"])
def notifications():

    if "pin" not in session:
        return jsonify({
            "success": False,
            "message": "Login required"
        })

    pin = session["pin"]

    cursor.execute("""
        SELECT branch, semester
        FROM student_data
        WHERE pin=%s
    """, (pin,))

    student = cursor.fetchone()

    branch = student["branch"]
    semester = str(student["semester"])

    cursor.execute("""
        SELECT
            id,
            title,
            message,
            category,
            created_at
        FROM notifications
        WHERE is_active=TRUE
        AND (
            target_branch='ALL'
            OR target_branch=%s
        )
        AND (
            target_semester='ALL'
            OR target_semester=%s
        )
        ORDER BY created_at DESC
    """, (branch, semester))

    notifications = cursor.fetchall()

    return jsonify({
        "success": True,
        "notifications": notifications
    })
  
# @app.route('/dashboard', methods=['GET'])
# def dashboard():

#     if 'pin' not in session:
#         return jsonify({
#             "success":False
#         })

#     pin = session['pin']

#     cursor.execute("""
#         SELECT pin,name,attendance,semester
#         FROM student_data
#         WHERE pin=%s
#     """,(pin,))

#     student = cursor.fetchone()

#     analysis = get_performance(pin)

#     next_class = get_next_class(student['semester'])

#     return jsonify({

#         "success":True,

#         "name":student['name'],
#         "pin":student['pin'],
#         "attendance":student['attendance'],

#         "performance":analysis['performance'],

#         "overall":analysis['overall'],

#         "weak_subject":analysis['weak_subject'],

#         "next_class":next_class
#     })

@app.route('/logout',methods=['POST'])
def logout():
    session.clear()
    return jsonify({
        "success":True
    })

@app.route('/chat', methods=['POST'])
def chat():

    if 'pin' not in session:
     return jsonify({
        "reply":"Please Login first"
    })

    data = request.get_json()

    user_message = data.get("message","").lower()


    pin = session.get('pin')
    
    if "hai" in user_message or "hello" in user_message or "hi" in user_message or "hey" in user_message:
        return jsonify({"reply": f"Hai, How is it going...?"})
    
    elif "pin" in user_message:
        return jsonify({"reply":f"Your PIN : {pin}"})
    
    elif "who teaches" in user_message or "who is handling" in user_message:
        cursor.execute("""
                       SELECT subject,staff_name,subject_code
                       FROM subjects
                       """)
        subjects = cursor.fetchall()
        for row in subjects:
            if row['subject'].lower() in user_message:
                return jsonify({
                    "reply":f"{row['subject']} is handled by {row['staff_name']}\n Subject Code : {row['subject_code']}"
                })
        return jsonify({
            "reply":"Subject Not Found"
            })
    elif "previous year papers" in user_message or "semester papers" in user_message:
        cursor.execute("""
            SELECT semester,branch
            FROM student_data
            WHERE pin=%s
            """,(pin,))
        student = cursor.fetchone()
        semester = student['semester']
        branch = student['branch']

        cursor.execute("""
            SELECT link 
            FROM papers
            WHERE branch=%s
            AND semester=%s
            """,(branch,semester))
        result=cursor.fetchone()
        if result:
            return jsonify({
            "reply": "Download Previous year papers",
            "url":result['link'],
            "link_text":"Click here"
             })
        else:
            return jsonify({"reply":"No previous paper found..."})
    elif "semester results" in user_message or "my result" in user_message or "semester marks" in user_message:
            cursor.execute("""
                SELECT semester
                FROM student_data
                WHERE pin=%s
                """,(pin,))

            student = cursor.fetchone()

            semester = student['semester']

            result = fetch_sbtet_result(
                pin,
                semester
                )

            if result['success']:

                return jsonify({
                "type":"sbtet_result",
                "title":"SBTET Result",
                "data":result
                })

            else:

                return jsonify({
                "reply":
                "Unable to fetch result.\n"
                + result['error']
                })
    elif "list all teachers" in user_message or "list teachers" in user_message or "my class faculty" in user_message:

        cursor.execute("""
            SELECT subject,staff_name,subject_code
            FROM subjects
            """)

        result = cursor.fetchall()

        return jsonify({
        "type":"teachers",
        "title":"Faculty Information",
        "data":result
    })
    elif "today classes" in user_message or "today class" in user_message:
        cursor.execute("""
        SELECT semester
        FROM student_data
        WHERE pin=%s
        """,(pin,))

        student = cursor.fetchone()
        semester = student['semester']
        
        today = datetime.now().strftime("%A")

        cursor.execute("""
            SELECT period_no, subject
        FROM timetable
        WHERE semester=%s
        AND day_name=%s
        ORDER BY period_no
        """,(semester,today))

        classes = cursor.fetchall()
        return jsonify({
        "type":"today_classes",
        "title":f"{today} Classes",
        "data":classes
})
    # elif "next class" in user_message or "upcoming class" in user_message:
    #     cursor.execute("""
    #         SELECT semester
    #         FROM student_data
    #         WHERE pin=%s
    #         """,(pin,))
    #     student = cursor.fetchone()
    #     semester = student['semester']
    #     periods = {
    #     1: (time(9,30), time(10,20)),
    #     2: (time(10,20), time(11,10)),
    #     3: (time(11,20), time(12,10)),
    #     4: (time(12,10), time(13,0)),
    #     5: (time(13,40), time(14,30)),
    #     6: (time(14,30), time(15,20)),
    #     7: (time(15,20), time(16,10))
    #     }

    #     current_time = datetime.now().time()
    #     today = datetime.now().strftime("%A")
    #     next_period = None
    #     for period, (start, end) in periods.items():
    #         if current_time < start:
    #             next_period = period
    #             break
    #     if not next_period:
    #         return jsonify({"reply":"No more classes for today 🎉"})
    #     else:
    #         cursor.execute("""
    #         SELECT subject
    #         FROM timetable
    #         WHERE semester=%s
    #         AND day_name=%s
    #         AND period_no=%s
    #         """,(semester,today,str(next_period)))

    #         result = cursor.fetchone()
    #         if not result:
    #             return jsonify({"reply":"No class found for next period..."})
    #         else:
    #             return jsonify({"reply":f"Your next class is {result['subject']} in Period {next_period}"})
    elif "attendance" in user_message:

        cursor.execute(
            """
            SELECT attendance
            FROM student_data
            WHERE pin=%s
            """,
            (pin,)
        )

        result = cursor.fetchone()
        if result['attendance'] <= 80 and result['attendance'] >=75:
            return jsonify({
            "reply":
            f"Your attendance is {result['attendance']}%\n You should be continue to college"})
        elif result['attendance'] <=75:
             return jsonify({
             "reply":
             f"Your attendance is {result['attendance']}%\n You must be continue to college otherwise you will be in condonation"})
        else:
             return jsonify({
             "reply":
             f"Your attendance is {result['attendance']}%"})
        
    elif "my details" in user_message:
        cursor.execute(
            """
            SELECT pin,name,branch
            FROM student_data
            WHERE pin=%s
            """,
            (pin,)
        )
        result = cursor.fetchone()
        return jsonify({"reply": f"PIN : {result['pin']} \nName : {result['name']} \nBranch : {result['branch']}"})
    elif "next class" in user_message or "upcoming class" in user_message:

        cursor.execute("""
        SELECT semester
        FROM student_data
        WHERE pin=%s
        """,(pin,))

        student = cursor.fetchone()
        next_class = get_next_class(student['semester'])

        return jsonify({
        "reply":f"Your next class is {next_class}"
        })
    elif "branch" in user_message:
        cursor.execute(
            """
            SELECT branch 
            FROM student_data
            WHERE pin=%s
            """,
            (pin,)
        )
        result = cursor.fetchone()
        return jsonify({
            "reply":f"You are in {result['branch']} Branch"
        })
    elif "timetable" in user_message:
        cursor.execute("""
            SELECT semester
            FROM student_data
            WHERE pin=%s
            """,(pin,))

        student = cursor.fetchone()

        semester = student['semester']

        cursor.execute("""
            SELECT *
            FROM timetable
            WHERE semester=%s
            """,(semester,))
    
        result = cursor.fetchall()
    
        return jsonify({
        "type":"timetable",
        "title":f"Semester {semester} Timetable",
        "data":result
        })
    elif "name" in user_message:

        cursor.execute(
            """
            SELECT name
            FROM student_data
            WHERE pin=%s
            """,
            (pin,)
        )

        result = cursor.fetchone()

        return jsonify({
            "reply":
            f"Your name is {result['name']}"
        })
    # elif "how am i doing" in user_message or "performance" in user_message or "analyze" in user_message \
    # or "work hard" in user_message:
    #     cursor.execute(
    #         """
    #         SELECT subject,final_avg
    #         FROM marks
    #         WHERE pin=%s
    #         """,
    #         (pin,)
    #     )
    #     results = cursor.fetchall()

    #     strong_subjects = []
    #     weak_subjects = []
    #     total = 0
    #     for row in results:
    #         avg = row['final_avg']
    #         total += avg
    #         if avg >= 35:
    #             strong_subjects.append(row['subject'])
    #         elif avg < 25:
    #             weak_subjects.append(row['subject'])
    #     overall = total/len(results)
    #     if overall >= 35:
    #         performance = "Excellent"       
    #     elif overall >= 28:
    #             performance = "Good"
    #     else :
    #             performance = "Average"
    #     reply = f"Your overall Performance is {performance}.\n\n"
    #     if weak_subjects:
    #         reply += "Need Improvement :\n"
    #         for sub in weak_subjects:
    #             reply += f". {sub}\n"
    #         reply += "\n"
    #         reply += "Suggestion :\n"
    #         reply += "Focus more on weak subjects and practice regularly"
    #     else:
    #             reply += "Great consistency across all subjects. Keep it up..."
    #     return jsonify({
    #             "reply":reply
    #         })
    elif "how am i doing" in user_message or "performance" in user_message  or "analyze" in user_message or "work hard" in user_message:

        analysis = get_performance(pin)

        reply = f"""Overall Performance : {analysis['performance']}
        Average Marks : {analysis['overall']}
        Weak Subject : {analysis['weak_subject']}
        """
        return jsonify({
        "reply":reply
        })
    elif "mid1" in user_message or "mid-1" in user_message or "mid_1" in user_message or "mid 1" in user_message:
        cursor.execute(
            """
            SELECT subject,mid1,mid1_avg
            FROM marks
            WHERE pin=%s
            """,
            (pin,)
        )

        result = cursor.fetchall()

        return jsonify({
            "type":"MID-1_Marks",
            "title":"MID-1 Marks",
            "data":result
        })
    
    elif "mid2" in user_message or "mid-2" in user_message or "mid_2" in user_message or "mid 2" in user_message:
        cursor.execute(
            """
            SELECT subject,mid2,mid2_avg
            FROM marks
            WHERE pin=%s
            """,
            (pin,)
        )
        result = cursor.fetchall()
        return jsonify({
            "type":"MID-2_Marks",
            "title":"MID-2 Marks",
            "data":result
        })

    elif "mid" in user_message or "midterm" in user_message:

        cursor.execute(
            """
            SELECT subject,mid1,mid2,final_avg
            FROM marks
            WHERE pin=%s
            """,
            (pin,)
        )

        result = cursor.fetchall()

        return jsonify({
          "type":"MID_Marks",
          "title":"MID Marks",
          "data":result
        })


    else:

        return jsonify({
            "reply":
            "Sorry, I couldn't understand."
        })
if __name__ == '__main__':
    app.run(debug=True, port=5000)