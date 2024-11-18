#本程序参考ClausewitzCPU0的wow-fishing，基于Yolov5修改
#下载yolov5后,安装依赖，训练模型

#启动程序后，把魔兽世界切换到前台即可，最好能启用钓鱼的全景视角（几乎成功率100%）

from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
from PIL import ImageGrab, Image
import imageio
import numpy as np
import time
import sys
import pyautogui
import audioop
import pyaudio
import torch

chunk = 1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,     #在windows的控制面板中，把声音->录音->立体声混音打开
                channels=2,  # need this to work (like other record script)
                rate=44100,
                input=True,
                frames_per_buffer=chunk,)
                # input_device_index=0)

RMS = 850                   #要根据自己的声卡进行优化，一般应在300以上。
# buf=40 # avoid boundary false trigger; not too far though
buf = 0  # alrdy compensated for boundary in initial rect adjustments
z = 0

model = torch.hub.load('.', 'custom', path='./best.pt',source="local") # 加载模型，具体路径以实际训练的模型为准
model.eval()

def AiFindFishingFloat():
    x,y=0,0        
    rect = GetWindowRect(GetForegroundWindow())
    rect = np.array(rect)
    print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'窗口大小：',rect) 
    rect_back = np.copy(rect)
    fish_area = (rect[0], rect[1], rect[2], rect[3])    
    time.sleep(.5)  # 等待鱼漂稳定，一般1秒左右
    pyautogui.moveTo(100, 100, 0.3)  #移动鱼漂到左上角，不影响识别
    time.sleep(1)  # TODO REMOVE
    print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'截图')
    img = ImageGrab.grab(fish_area)
    img.save('wowDemoFishing3.jpg')  # Saving the image    
    
    img = './wowDemoFishing3.jpg' # 需要被推理的图片
    results = model(img)    
    detections = results.xyxy[0]      
    SLIDER_CLASS_INDEX = 0    
    slider_boxes = []
    for *box, conf, cls in detections:
        if cls == SLIDER_CLASS_INDEX:
            x1, y1, x2, y2 = map(int, box)
            slider_boxes.append((x1, y1, x2, y2))
    
    for i, box in enumerate(slider_boxes):
        print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),f'Slider {i+1}: {box}')
        x=int((box[0]+box[2])/2)
        y=int((box[1]+box[3])/2)
        print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'中间点坐标：',x,"，",y)
    return x,y 

def MonitorSound():
    print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'开始检测声音')
    ret=False

    t1 = time.time()    
    # 返回片段的均方根，即sqrt(sum(S_i^2)/n)。
    # 这是衡量音频信号功率的指标。
    rms = 0
    n = 0    
    while 1:
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)  # width=2 for format=paInt16
        if n == 10:  # only print out every 10th one                      #测试用的，可删除这段
            #print('%d' % n,"当前时间: {}".format(time.asctime(time.localtime(time.time()))),'rms value = %d' % rms)
            n = 0
        else:
            n = n + 1                     
        #print('%d' % n,"当前时间: {}".format(time.asctime(time.localtime(time.time()))),'rms value = %d' % rms)

        if rms > RMS:            
            if time.time() - t1 > 1.0:
                print("上钩时间: {}".format(time.asctime(time.localtime(time.time()))),'rms value = %d' % rms)               
                ret=True
                break  # out of while 1
        if (time.time() - t1 > 22.0):  # it never caught; break out of while
            print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'FISH CATCH NEVER SOUNDED or something else went wrong.')
            ret=False
            break
        time.sleep(.3)    
    #print('AUDIO TRIGGERED!!!! rms value = %d' % rms)
    #time.sleep(0.1)  # 建议增加随机时间
    return ret

def main():      
    while True:
        if GetWindowText(GetForegroundWindow()) != '魔兽世界':
            print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'请激活魔兽世界界面 !')
            time.sleep(2)
        else:            
            print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),'找到魔兽世界！')
            rd=np.random.randint(51)/10
            print(rd)
            time.sleep(rd+1)
            pyautogui.press('9')  #在游戏中将钓鱼技能拖到9号技能
            print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),"抛竿！")
            time.sleep(1)
            ix,iy=AiFindFishingFloat()
            if ix>0 and iy>0:
                print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),"鱼漂位置：",ix,iy)
                pyautogui.moveTo(ix-10, iy-10, 0.3)
                time.sleep(0.3)
            
                if MonitorSound()==True:
                    print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),"通过声音判断，鱼已上钩")
                    pyautogui.mouseDown(button='right')
                    #pyautogui.rightClick()
                    print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),"起鱼")
                    pyautogui.mouseUp(button='right')
                    time.sleep(0.5)   #等待一会儿
                    #pyautogui.moveTo(100, 100, 0.5)
            else:
                print("当前时间: {}".format(time.asctime(time.localtime(time.time()))),"没找到鱼漂！")                  
                
    #print("main stop!") 

if __name__=='__main__':
    main()
