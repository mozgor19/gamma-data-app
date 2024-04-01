import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QStyle, QSlider, QLabel, QGroupBox, QSizePolicy, QLineEdit, QMessageBox, QTabWidget, QGridLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QTimer, Qt, QUrl
from PyQt5.QtGui import QIcon
from pytube import YouTube
from saveFrames import save_frames

class VideoPlayerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ITU GAMMA Data Collecting App")
        self.setGeometry(100, 100, 800, 600)

        self.setWindowIcon(QIcon("gammabird.ico"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 360)
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.btn_open = QPushButton("Open Video")

        self.btn_play = QPushButton()
        self.btn_pause = QPushButton()
        self.btn_stop = QPushButton()
        self.slider = QSlider(Qt.Horizontal)
        self.lbl_duration = QLabel()
        self.lbl_position = QLabel()
        
        self.btn_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.btn_pause.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.btn_stop.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_play)
        button_layout.addWidget(self.btn_pause)
        button_layout.addWidget(self.btn_stop)

        button_group = QGroupBox()
        button_group.setLayout(button_layout)

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.lbl_position)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.lbl_duration)

        slider_group = QGroupBox()
        slider_group.setLayout(slider_layout)

        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.video_widget)
        vbox_layout.addWidget(slider_group)
        vbox_layout.addWidget(button_group)
        vbox_layout.addWidget(self.btn_open)

        self.tab_widget = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab1, "Open Video")
        self.tab_widget.addTab(self.tab2, "Download and Crop Video")
        self.tab_widget.addTab(self.tab3, "Save Frames")

        self.tab1_layout = QVBoxLayout()
        self.tab1_layout.addLayout(vbox_layout)
        self.tab1.setLayout(self.tab1_layout)

        self.tab2_layout = QVBoxLayout()
        self.tab2.setLayout(self.tab2_layout)

        self.tab3_layout = QVBoxLayout()
        self.tab3.setLayout(self.tab3_layout)

        self.link_edit = QLineEdit()
        self.start_time_edit = QLineEdit()
        self.end_time_edit = QLineEdit()
        self.btn_crop_save = QPushButton("Crop and Save")

        self.download_btn = QPushButton("Download")
        self.btn_select_output_folder = QPushButton("Select Output Folder")

        self.download_btn.clicked.connect(self.download_video)
        self.btn_select_output_folder.clicked.connect(self.select_output_folder)
        self.btn_crop_save.clicked.connect(self.crop_and_save_video)

        download_layout = QGridLayout()
        download_layout.addWidget(QLabel("Video URL:"), 0, 0)
        download_layout.addWidget(self.link_edit, 0, 1)
        download_layout.addWidget(self.btn_select_output_folder, 0, 2)
        download_layout.addWidget(self.download_btn, 0, 3)
        download_layout.addWidget(QLabel("Start Time (MM:SS):"), 1, 0)
        download_layout.addWidget(self.start_time_edit, 1, 1)
        download_layout.addWidget(QLabel("End Time (MM:SS):"), 2, 0)
        download_layout.addWidget(self.end_time_edit, 2, 1)
        download_layout.addWidget(self.btn_crop_save, 3, 0, 1, 2)
        self.tab2_layout.addLayout(download_layout)

        self.video_path_edit = QLineEdit()
        self.output_folder_edit = QLineEdit()
        self.frame_interval_edit = QLineEdit()

        self.btn_browse_video = QPushButton("Browse Video")
        self.btn_browse_output = QPushButton("Browse Output Folder")
        self.btn_save_frames = QPushButton("Save Frames")

        self.btn_browse_video.clicked.connect(self.browse_video)
        self.btn_browse_output.clicked.connect(self.browse_output)
        self.btn_save_frames.clicked.connect(self.save_frames)

        save_frame_layout = QGridLayout()
        save_frame_layout.addWidget(QLabel("Video Path:"), 0, 0)
        save_frame_layout.addWidget(self.video_path_edit, 0, 1)
        save_frame_layout.addWidget(self.btn_browse_video, 0, 2)
        save_frame_layout.addWidget(QLabel("Output Folder:"), 1, 0)
        save_frame_layout.addWidget(self.output_folder_edit, 1, 1)
        save_frame_layout.addWidget(self.btn_browse_output, 1, 2)
        save_frame_layout.addWidget(QLabel("Frame Interval:"), 2, 0)
        save_frame_layout.addWidget(self.frame_interval_edit, 2, 1)
        save_frame_layout.addWidget(self.btn_save_frames, 3, 0, 1, 2)
        self.tab3_layout.addLayout(save_frame_layout)

        self.central_layout = QVBoxLayout()
        self.central_layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.central_layout)

        self.video_source = None
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.btn_open.clicked.connect(self.open_video)
        self.btn_play.clicked.connect(self.play_video)
        self.btn_pause.clicked.connect(self.pause_video)
        self.btn_stop.clicked.connect(self.stop_video)

        self.slider.sliderMoved.connect(self.set_position)

        self.download_count = 0  # Download sayacını başlat
        self.cropped_count = 0  # Kırpma sayacını başlat

        self.output_folder_label = QLabel()
        self.output_folder_label.setText(f"Output Folder: {os.path.join(os.path.expanduser('~'), 'Desktop', 'IHA Video')}")
        self.tab2_layout.addWidget(self.output_folder_label)

    def open_video(self):
        default_path = os.path.join(os.path.expanduser("~"), "Desktop", "IHA Video")
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video File", default_path, "Video Files (*.mp4 *.avi)")
        if filename:
            self.video_source = filename
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_source)))
            self.play_video()

    def play_video(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.player.setPosition(0)
        self.player.play()
        self.timer.start(30)

    def pause_video(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.timer.stop()

    def stop_video(self):
        if self.player.state() != QMediaPlayer.StoppedState:
            self.player.stop()
            self.timer.stop()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
                self.timer.stop()
            else:
                self.player.play()
                self.timer.start(30)

    def set_position(self, position):
        self.player.setPosition(position)

    def update_frame(self):
        if self.player.duration() > 0:
            self.slider.setMaximum(self.player.duration())
            self.slider.setValue(self.player.position())
            duration = self.player.duration() / 1000
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.lbl_duration.setText(f"{minutes:02d}:{seconds:02d}")
            position = self.player.position() / 1000
            minutes = int(position // 60)
            seconds = int(position % 60)
            self.lbl_position.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.slider.setMaximum(0)
            self.slider.setValue(0)
            self.lbl_duration.setText("00:00")
            self.lbl_position.setText("00:00")

    def download_video(self):
        video_url = self.link_edit.text()
        if not video_url:
            QMessageBox.warning(self, "Warning", "Please enter a valid video URL.")
            return
    
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

            output_folder = self.output_folder_edit.text()
            if not output_folder:
                output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "IHA Video")
            
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            self.download_count = self.get_last_download_count(output_folder) + 1
            filename = f"iha_video-{self.download_count}.mp4"
            while os.path.exists(os.path.join(output_folder, filename)):
                self.download_count += 1
                filename = f"iha_video-{self.download_count}.mp4"

            stream.download(output_path=output_folder, filename=filename)
            QMessageBox.information(self, "Success", "Video downloaded successfully!")
            self.save_last_download_count(output_folder, self.download_count)
            self.output_folder_label.setText(f"Output Folder: {output_folder}")  # Dizin bilgisini güncelle
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def select_output_folder(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if output_folder:
            self.output_folder_edit.setText(output_folder)

    def get_last_download_count(self, output_folder):
        files = [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f)) and f.startswith("iha_video-")]
        if files:
            last_file = sorted(files)[-1]
            count = int(last_file.split("-")[1].split(".")[0])  # Dosya adından sayıyı al
            return count
        else:
            return 0

    def save_last_download_count(self, output_folder, count):
        files = [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f)) and f.startswith("iha_video-")]
        if files:
            last_file = sorted(files)[-1]
            os.rename(os.path.join(output_folder, last_file), os.path.join(output_folder, f"iha_video-{count}.mp4"))
    
    def get_last_download_count_cropped(self, output_folder):
        cropped_files = [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f)) and f.endswith("-cropped")]
        if cropped_files:
            last_cropped_file = sorted(cropped_files)[-1]
            count = int(last_cropped_file.split("-")[1].split("-cropped.mp4")[0])  # Dosya adından sayıyı al
            return count
        else:
            return 0
    
    def save_last_download_count_cropped(self, output_folder, count):
        cropped_files = [f for f in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, f)) and f.endswith("-cropped.mp4")]
        if cropped_files:
            last_cropped_file = sorted(cropped_files)[-1]
            new_filename = f"iha_video-{count}-cropped.mp4"
            os.rename(os.path.join(output_folder, last_cropped_file), os.path.join(output_folder, new_filename))

    
    def crop_and_save_video(self):
        if self.video_source is None:
            QMessageBox.warning(self, "Warning", "First open a video!")
            return
    
        start_time_input = self.start_time_edit.text()
        end_time_input = self.end_time_edit.text()

        try:
            start_time_minutes, start_time_seconds = map(int, start_time_input.split(":"))
            end_time_minutes, end_time_seconds = map(int, end_time_input.split(":"))

            start_time_seconds_total = start_time_minutes * 60 + start_time_seconds
            end_time_seconds_total = end_time_minutes * 60 + end_time_seconds

            video_duration = self.player.duration() // 1000  # Video süresi saniye cinsinden

            if start_time_seconds_total >= end_time_seconds_total:
                raise ValueError("Start time cannot be greater than or equal to end time.")
            if end_time_seconds_total > video_duration:
                raise ValueError("End time cannot be greater than video duration.")

            output_folder = self.output_folder_edit.text()
            if not output_folder:
                output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "IHA Video")
        
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            self.cropped_count = self.get_last_download_count_cropped(output_folder) + 1
            filename = f"iha_video-{self.cropped_count}-cropped.mp4"
            while os.path.exists(os.path.join(output_folder, filename)):
                self.cropped_count += 1
                filename = f"iha_video-{self.cropped_count}-cropped.mp4"

            # Başlangıçtan önceki siyah ekranı kesmek için komut
            command = f"ffmpeg -ss {start_time_input} -i '{self.video_source}' -to {end_time_input} -c copy '{os.path.join(output_folder, filename)}'"
            os.system(command)

            QMessageBox.information(self, "Success", "Video cropped and saved!")
            self.save_last_download_count_cropped(output_folder, self.cropped_count)
            self.output_folder_label.setText(f"Output Folder: {output_folder}")  # Dizin bilgisini güncelle

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    
    def browse_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi)")
        if video_path:
            self.video_path_edit.setText(video_path)

    def browse_output(self):
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if output_folder:
            self.output_folder_edit.setText(output_folder)

    def save_frames(self):
        video_path = self.video_path_edit.text()
        output_folder = self.output_folder_edit.text()
        frame_interval = self.frame_interval_edit.text()

        if not output_folder:
            output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "IHA Video Frames")
    
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        if not video_path or not frame_interval:
            QMessageBox.warning(self, "Warning", "Please enter video path and frame interval.")
            return

        try:
            frame_interval = int(frame_interval)
            frame_count = save_frames(video_path, output_folder, frame_interval)
            QMessageBox.information(self, "Success", f"{frame_count} frames saved successfully!")
        except ValueError:
            QMessageBox.warning(self, "Warning", "Please enter a valid frame interval (integer value).")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


    def closeEvent(self, event):
        self.stop_video()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('gammabird.png'))
    player = VideoPlayerApp()
    player.show()
    sys.exit(app.exec_())
