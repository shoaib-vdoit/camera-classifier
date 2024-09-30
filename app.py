import tkinter as tk
from tkinter import simpledialog
import cv2 as cv
import os
import PIL.Image, PIL.ImageTk
import camera
import model

class App:
    def __init__(self, window=tk.Tk(), window_title="Camera Classifier"):
        self.window = window
        self.window.title(window_title)
        self.counters = [1, 1]

        self.model = model.Model()

        self.auto_predict = False
        self.camera = camera.Camera()

        self.init_gui()
        
        self.delay = 15
        self.update()

        self.window.attributes('-topmost', True)
        self.window.mainloop()

    def init_gui(self):
        self.window.configure(bg="#2C3E50")  # Set background color

        # Create a frame for better organization
        main_frame = tk.Frame(self.window, bg="#2C3E50")
        main_frame.pack(padx=20, pady=20)

        # Create a canvas for displaying camera frames
        self.canvas = tk.Canvas(main_frame, width=self.camera.width, height=self.camera.height, bg="#34495E")
        self.canvas.pack()

        # Create a button for toggling autoprediction
        self.btn_toggleauto = tk.Button(main_frame, text="Auto Prediction", width=30, command=self.auto_predict_toggle,
                                        bg="#3498DB", fg="white", pady=5)
        self.btn_toggleauto.pack(side=tk.TOP, pady=10)

        # Ask the user to enter names of two classes
        self.classname_one = simpledialog.askstring("Classname one", "Enter the name of the first class", parent=self.window)
        self.classname_two = simpledialog.askstring("Classname two", "Enter the name of the second class", parent=self.window)

        # Create buttons for saving the images of each class
        self.btn_class_one = tk.Button(main_frame, text=self.classname_one, width=30, command=lambda: self.save_for_class(1),
                                       bg="#27AE60", fg="white", pady=5)
        self.btn_class_one.pack(side=tk.LEFT, padx=5)

        self.btn_class_two = tk.Button(main_frame, text=self.classname_two, width=30, command=lambda: self.save_for_class(2),
                                       bg="#E74C3C", fg="white", pady=5)
        self.btn_class_two.pack(side=tk.RIGHT, padx=5)

        # Create a button for training model
        self.btn_train = tk.Button(main_frame, text="Train Model", width=30, command=lambda: self.model.train_model(self.counters),
                                   bg="#F39C12", fg="white", pady=5)
        self.btn_train.pack(side=tk.TOP, pady=10)

        # Create a button for making prediction
        self.btn_predict = tk.Button(main_frame, text="Predict", width=30, command=self.predict, bg="#8E44AD", fg="white", pady=5)
        self.btn_predict.pack(side=tk.TOP, pady=10)

        # Create a button for reset
        self.btn_reset = tk.Button(main_frame, text="Reset", width=30, command=self.reset, bg="#BDC3C7", fg="#2C3E50", pady=5)
        self.btn_reset.pack(side=tk.BOTTOM, pady=10)

        # Create a label with text CLASS
        self.class_label = tk.Label(main_frame, text="CLASS", font=("Helvetica", 20), bg="#2C3E50", fg="white")
        self.class_label.pack(side=tk.BOTTOM, pady=10)

    def auto_predict_toggle(self):
        self.auto_predict = not self.auto_predict

    def save_for_class(self, class_num):
        ret, frame = self.camera.get_frame()
        if not os.path.exists('1'):
            os.mkdir('1')
        if not os.path.exists('2'):
            os.mkdir('2')

        cv.imwrite(f'{class_num}/frame{self.counters[class_num - 1]}.jpg', cv.cvtColor(frame, cv.COLOR_RGB2GRAY))
        img = PIL.Image.open(f'{class_num}/frame{self.counters[class_num - 1]}.jpg')
        img.thumbnail((150, 150), PIL.Image.Resampling.LANCZOS)
        img.save(f'{class_num}/frame{self.counters[class_num - 1]}.jpg')

        self.counters[class_num - 1] += 1

    def reset(self):
        # removes all files in directory 1 and 2
        for directory in ['1', '2']:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

        # reset the counter value to 1,1
        self.counters = [1, 1]

        self.model = model.Model()

        # set the text of the label widget to 'CLASS'
        self.class_label.config(text='CLASS')

    def update(self):
        if self.auto_predict:
            self.predict()

        # get the frame from the camera
        ret, frame = self.camera.get_frame()

        # if the frame is successfully obtained
        if ret:
            # convert the image to a tkinter photoimage
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # schedule the update method to be called after a delay
        self.window.after(self.delay, self.update)

    def predict(self):
        frame = self.camera.get_frame()
        prediction = self.model.predict(frame)

        if prediction == 1:
            self.class_label.config(text=self.classname_one)
            return self.classname_one
        if prediction == 2:
            self.class_label.config(text=self.classname_two)
            return self.classname_two


