from flask import Flask, render_template, Response
import cv2
import socket
import numpy as np
import time

class MyClient():
    def __init__(self) -> None:
        self.my_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.my_socket.connect(('127.0.0.1',8234)) # 服务端ip和端口

    def get_img(self):
        msg = "识别图像"
        # 防止输入空消息
        if not msg:
            return
        self.my_socket.send(msg.encode('utf-8'))  # 收发消息一定要二进制，记得编码
        if msg == '识别图像':
            img_data = self.my_socket.recv(4500000)   # 这个数字要大于图片的长宽之积，否则会报错
            if img_data == b'None':
                print('无图像')
                return
            # 将 图片字节码bytes  转换成一维的numpy数组 到缓存中
            img_buffer_numpy = np.frombuffer(img_data, dtype=np.uint8) 
        return img_buffer_numpy
            

app = Flask(__name__)
my_client = MyClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')

def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames():
    while True:
        #ret, frame = cap.read()  # 读取视频帧
        buffer = my_client.get_img()
        if buffer is None:
            print('空图像')
            continue
        else:
            # 将帧转换为图像数据
            #ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)
    #cap.release()

if __name__ == '__main__':
	app.run(debug=True)


