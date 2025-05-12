from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
import cv2
import os
from datetime import datetime
import csv

class Recognition_Face:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1530x790+0+0")
        self.root.title("Face Recognition Attendance System")
        self.root.config(bg="white")
        self.root.wm_iconbitmap("face.ico")
        self.webcam_active = False

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        title = Label(self.root, text="FACE RECOGNITION", font=("times new roman", 30, "bold"),
                      bg="white", fg="crimson")
        title.place(x=0, y=0, width=1530, height=50)

        Back_Button = Button(title, text="Back", command=self.go_back,
                             font=("arial", 11, "bold"), width=17, bg="white", fg="red")
        Back_Button.pack(side=RIGHT)

        title1 = Label(self.root, text="Frontal Face Recognition", font=("times new roman", 20, "bold"),
                       bg="white", fg="blue")
        title1.pack(side=BOTTOM, fill=X)

        img_logo11 = Image.open("college_images/2-AI-invades-automobile-industry-in-2019.jpeg").resize((650, 700), Image.LANCZOS)
        self.photoImg_logo11 = ImageTk.PhotoImage(img_logo11)
        Label(self.root, image=self.photoImg_logo11, bd=20).place(x=0, y=40, width=650, height=700)

        img_logo = Image.open("college_images/facial-recognition-face-id-password-6.jpg").resize((950, 700), Image.LANCZOS)
        self.photoImg_logo1 = ImageTk.PhotoImage(img_logo)
        bg_lbl = Label(self.root, image=self.photoImg_logo1, bd=20)
        bg_lbl.place(x=500, y=40, width=950, height=700)

        Button(bg_lbl, text="Face Recognition", command=self.detect_face, borderwidth=6,
               font=("times new roman", 18, "bold"),
               bg="black", activebackground="red", fg="gold", cursor="hand2").place(x=20, y=300, width=200, height=40)

    def mark_attendance(self, student_id, roll, department, name):
        filename = "present.csv"
        date_str = datetime.now().strftime("%d/%m/%Y")
        already_marked = False

        # Create file if not exists
        if not os.path.exists(filename):
            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Roll", "Name", "Department", "Time", "Date", "Status"])

        # Check if student is already marked for today
        with open(filename, "r") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0] == str(student_id) and row[5] == date_str:
                    already_marked = True
                    break

        if not already_marked:
            now = datetime.now()
            time_str = now.strftime("%H:%M:%S")
            with open(filename, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([student_id, roll, name, department, time_str, date_str, "Present"])
            print(f"[INFO] Attendance marked for: {name}")

    def detect_face(self):
        if self.webcam_active:
            return

        self.webcam_active = True

        if not os.path.exists("haarcascade_frontalface_default.xml") or not os.path.exists("classifier.xml"):
            messagebox.showerror("Missing File", "Classifier or Haarcascade file missing")
            self.webcam_active = False
            return

        faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        clf = cv2.face.LBPHFaceRecognizer_create()
        clf.read("classifier.xml")
        Video_Capture = cv2.VideoCapture(0)

        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, clf):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = classifier.detectMultiScale(gray, scaleFactor, minNeighbors)

            for (x, y, w, h) in faces:
                id, pred = clf.predict(gray[y:y+h, x:x+w])
                confidence = int(100 * (1 - pred / 300))

                try:
                    conn = mysql.connector.connect(
                        host='localhost',
                        username='root',
                        password='Rolta@123',
                        database='facial_recognition'
                    )
                    cursor = conn.cursor()
                    cursor.execute("SELECT student_id, roll, student_name, department FROM new_student WHERE id=%s", (id,))
                    result = cursor.fetchone()
                    conn.close()

                    if result and confidence > 77:
                        student_id, roll, name, department = result
                        cv2.rectangle(img, (x, y), (x+w, y+h), color, 3)
                        cv2.putText(img, f"ID: {student_id}", (x, y - 80), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(img, f"Roll: {roll}", (x, y - 55), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(img, f"Name: {name}", (x, y - 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        cv2.putText(img, f"Dept: {department}", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2)
                        print(f"[DEBUG] Detected and marking attendance for: {name}")
                        self.mark_attendance(student_id, roll, department, name)
                    else:
                        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3)
                        cv2.putText(img, "Unknown", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                except mysql.connector.Error as err:
                    print(f"[ERROR] Database error: {err}")
                except Exception as e:
                    print(f"[ERROR] Unexpected error: {e}")

        def recognize(img, clf, faceCascade):
            draw_boundary(img, faceCascade, 1.1, 10, (0, 255, 0), clf)
            return img

        while self.webcam_active:
            ret, frame = Video_Capture.read()
            if not ret:
                break
            frame = recognize(frame, clf, faceCascade)
            cv2.imshow("Face Detector", frame)

            key = cv2.waitKey(1)
            if key == 13 or cv2.getWindowProperty("Face Detector", cv2.WND_PROP_VISIBLE) < 1:
                break

        self.close_webcam(Video_Capture)

    def close_webcam(self, Video_Capture):
        Video_Capture.release()
        cv2.destroyAllWindows()
        self.webcam_active = False
        messagebox.showinfo("Attendance", "Attendance has been saved successfully", parent=self.root)

    def go_back(self):
        if self.webcam_active:
            cv2.destroyAllWindows()
        self.root.destroy()

    def on_closing(self):
        if self.webcam_active:
            cv2.destroyAllWindows()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = Recognition_Face(root)
    root.mainloop()
