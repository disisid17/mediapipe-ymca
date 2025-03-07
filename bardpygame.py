import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import joblib
import imutils
import argparse
import copy
import pygame
import threading
import sys
import random
from random import choice
import time


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
HOVER = (125, 125, 125)
YELLOW = (255, 255, 0)
DEFAULT_IMAGE_WIDTH = 1200
X_TRANSLATION_PIXELS = 200
Z_TRANSLATION_PIXELS = 100
cap = cv2.VideoCapture(0)
mp_drawing = mp.solutions.drawing_utils  # Drawing helpers
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose_lock = threading.Lock()
last_call_time = None
call_time = None
font = None
def randcol():#define a completely random color generator with all possible colors
    colo1 = choice("abcdef1234567890")
    colo2 = choice("abcdef1234567890")
    colo3 = choice("abcdef1234567890")
    colo4 = choice("abcdef1234567890")
    colo5 = choice("abcdef1234567890")
    colo6 = choice("abcdef1234567890")
    hexe = str("#"+colo1+colo2+colo3+colo4 +colo5 +colo6 )
    value = hexe.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i +lv//3],16) for i in range(0,lv,lv//3))
def texer(surface,text,color, fonts,x,y):
    font = pygame.font.Font("./mediapipe-ymca/ComicSansMS3.ttf", int(fonts/1.25))
    text_surface = font.render(text,True,color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surface.blit(text_surface,text_rect)
    pass
def fps():
    global call_time
    if call_time == None:
        call_time = time.time()
    else:
        ret = time.time() - call_time
        call_time = time.time()
        perSec = 1/ret
        perSec = round(perSec/5,0)
        perSec = perSec * 5
        return perSec
def last():
    """
 Returns the time since the last call to this function.

 If this is the first time the function is called, it returns 0.

 Returns:
   float: The time in seconds since the last call to this function.
 """
    global last_call_time
    now = time.time()
    if last_call_time is None:
        last_call_time = now
        return 0
    else:
        elapsed_time = now - last_call_time
        last_call_time = now
        return elapsed_time


def since():
    """
 Returns the timestamp of the last call to the "last" function.

 This function does not reset the timer like the "last" function.

 Returns:
   float: The timestamp of the last call to the "last" function.
 """
    global last_call_time
    return time.time() - last_call_time

"""
Usage:

python 03_pose_predictions.py --model-name best_ymca_pose_model

python 03_pose_predictions.py 
"""
pygame.init()
def retpose():
            body_language_class = ''
            global model
            global cap
            with pose_lock:
                ret, frame = cap.read()
                #frame = cv2.flip(frame,1)
                frame = imutils.resize(frame, width=DEFAULT_IMAGE_WIDTH)

                # Recolor Feed
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make Detections
                results = pose.process(image)

                # Recolor image back to BGR for rendering
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                

                # 4. Pose Detections
                
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                                        mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                        )
                # Export coordinates
                try:
                    # Extract Pose landmarks
                    landmarks = results.pose_landmarks.landmark
                    arm_landmarks = []
                    pose_index = mp_pose.PoseLandmark.LEFT_SHOULDER.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    pose_index = mp_pose.PoseLandmark.RIGHT_SHOULDER.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    pose_index = mp_pose.PoseLandmark.LEFT_ELBOW.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    pose_index = mp_pose.PoseLandmark.RIGHT_ELBOW.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    pose_index = mp_pose.PoseLandmark.LEFT_WRIST.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    pose_index = mp_pose.PoseLandmark.RIGHT_WRIST.value
                    arm_landmarks += [landmarks[pose_index].x, landmarks[pose_index].y, landmarks[pose_index].z]

                    row = np.around(arm_landmarks, decimals=9).tolist()

                    # Make Detections
                    X = pd.DataFrame([row])
                    body_language_class = model.predict(X)[0]
                    body_language_prob = model.predict_proba(X)[0]
                    #print(body_language_class, np.around(body_language_prob, decimals=3))

                    

                    # Get status box
                    status_width = 250
                    if False:
                        status_width = 500
                    cv2.rectangle(image, (0, 0), (status_width, 60), (245, 117, 16), -1)

                    # Display Class
                    cv2.putText(image, 'CLASS'
                                , (95, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, body_language_class.split(' ')[0]
                                , (90, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                    # Display Probability
                    cv2.putText(image, 'PROB'
                                , (15, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(round(body_language_prob[np.argmax(body_language_prob)], 2))
                                , (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    # Display FPS
                    cv2.putText(image, 'FPS'
                                , (205, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(round(fps()))
                                , (200, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                except Exception as exc:
                    pass

                return image,body_language_class


# Font set

def multi(string: str, font, rect, fontColour, BGColour, justification=0):
    """Returns a surface containing the passed text string, reformatted
        to fit within the given rect, word-wrapping as necessary. The text
        will be anti-aliased.

        Parameters
        ----------
        string - the text you wish to render. \n begins a new line.
        font - a Font object
        rect - a rect style giving the size of the surface requested.
        fontColour - a three-byte tuple of the rgb value of the
                text color. ex (0, 0, 0) = BLACK
        BGColour - a three-byte tuple of the rgb value of the surface.
        justification - 0 (default) left-justified
                    1 horizontally centered
                    2 right-justified

        Returns
        -------
        Success - a surface object with the text rendered onto it.
        Failure - raises a TextRectException if the text won't fit onto the surface.
        """

    requestedLines = string.splitlines()
    # Create a series of lines that will fit on the provided
    # rectangle.

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(BGColour)
    fromt = 0
    for text in requestedLines:
        temp = font.render(text, 1, fontColour)
        surface.blit(temp, (rect.width / 2 - temp.get_width() / 2, fromt))
        fromt += font.size(text)[1]
    return surface


# Define button class
class Button:
    global font
    def __init__(self, x, y, width, height, color=BLACK, text='', text_color=BLACK, fonts=36, oc=WHITE, round=True, thi= 10):
        self.scale = swi / 800
        x = x * self.scale
        y = y * self.scale * 4 / 5
        self.x = x
        self.y = y
        self.width = width * self.scale
        self.height = height * self.scale
        fonts = int(self.scale * fonts)
        self.font = pygame.font.Font("./mediapipe-ymca/ComicSansMS3.ttf", int(fonts/1.25))
        font = pygame.font.Font("./mediapipe-ymca/ComicSansMS3.ttf", int(fonts/1.25))
        self.rects = pygame.Rect(x - self.width * 0.025, y - self.width * 0.025, self.width * 1.05,
                                 self.height + self.width * 0.05)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.thi = thi
        
        self.oc = oc
        self.color = color
        self.text = text
        self.text_color = text_color
        self.make = True
        self.calls = 0
        if not round:
            self.scale = 0

    def draw(self, surface, ml=False,newt=None):
        if (newt !=None) :
            #print(newt)
            self.text = newt
            self.text_color = randcol()
        if self.calls == 0:
            #print(self.text)
            
            self.calls += 1
        if self.make:
            if self.oc:
                pass
                pygame.draw.rect(surface, self.oc, self.rects, 0, border_radius=int(self.scale * self.thi))
            
            pygame.draw.rect(surface, self.color, self.rect, 0, border_radius=int(self.scale * self.thi))

            if self.text != '':
                if not ml:
                    text_surface = self.font.render(self.text, True, self.text_color)
                    text_rect = text_surface.get_rect()
                    text_rect.center = self.rect.center
                    surface.blit(text_surface, text_rect)
                if ml:
                    text_surface = multi(self.text, self.font, self.rect, self.text_color, self.color)
                    text_rect = text_surface.get_rect()
                    text_rect.center = self.rect.center
                    surface.blit(text_surface, (self.x, self.y))

    def texty(self, surface, tex="", coord=(0, 0)):
        if self.make:
            pygame.draw.rect(surface, WHITE, self.rect, 0, border_radius=int(self.scale * 10))
            pygame.draw.rect(surface, WHITE, self.rect, 0, border_radius=int(self.scale * 10))
            if self.text != '':
                text_surface = self.font.render(tex, True, RED)
                text_rect = text_surface.get_rect()
                text_rect.center = self.rect.center
                surface.blit(text_surface, coord)

    def rem(self):
        self.make = False

    def is_hover(self, pos):
        return self.rect.collidepoint(pos)


# Function to create buttons
def create_buttons():
    easy_button = Button(100, 225, 200, 50, GREEN, 'Easy', oc=GREEN)
    medium_button = Button(100, 325, 200, 50, BLUE, 'Medium', oc=YELLOW)
    hard_button = Button(100, 425, 200, 50, RED, 'Hard', oc=RED)
    
    return [easy_button, medium_button, hard_button]


def level_select_screen():
    screen.fill(BLUE)
    l1 = Button(300, 150, 200, 50, GREEN, "YMCA", oc=GREEN)
    l2 = Button(300, 250, 200, 50, BLACK, "Level 2", oc=YELLOW)
    hard_button = Button(300, 350, 200, 50, RED, 'Level 3', oc=RED)
    return [l1, l2, hard_button]
    # pygame.display.flip()


def exitb():
    screen.fill(HOVER)
    return Button(300, 250, 400, 100, WHITE, "Restart?", oc=RED)


def main_menu():
    running = True
    dif = 0
    lev = 0
    buttons = create_buttons()
    levs = level_select_screen()
    welc = Button(300, 50, 200, 100, WHITE, "Welcome to Dance-off!", RED, fonts=60)
    info = Button(720, 40, 20, 20, WHITE, 'i',oc = BLACK,thi = 20,fonts = 20)
    difsel = False
    levsel = False
    while not levsel:

        if not difsel:
            screen.fill(WHITE)
        else:
            screen.fill(BLUE)
        mouse_pos = pygame.mouse.get_pos()
        if not difsel:

            welc.draw(screen)
            info.draw(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button.is_hover(mouse_pos) and button.make:
                            if True:
                                if button.text == 'Easy':
                                    dif = 3
                                elif button.text == 'Medium':
                                    dif = 2
                                else:
                                    dif = 1
                                #button.rem()
                            print(f"Clicked {button.text} difficulty")
                            difsel = True
            for button in buttons:
                if button.is_hover(mouse_pos):
                    button.color = HOVER
                else:
                    button.color = WHITE

                button.draw(screen)

        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in levs:
                        if button.is_hover(mouse_pos) and button.make:
                            if True:
                                if button.text == 'YMCA':
                                    lev = 1
                                elif button.text == 'Level 2':
                                    lev = 2
                                else:
                                    lev = 3
                                button.rem()
                            print(f"Clicked {button.text}")
                            levsel = True
            for button in levs:
                if button.is_hover(mouse_pos):
                    button.color = HOVER
                else:
                    button.color = WHITE
                button.draw(screen)

        pygame.display.flip()
    return lev, dif

def score(mult, times):
    sut = 0
    scale = 8 * len(times)
    for i in times:
        sut += i[1]
    scale = sut / scale

    sut = round((scale * 50000), 3) * mult
    print(sut)
    return sut


def leva(lev):
    with open(f'./mediapipe-ymca/models/level{lev}_pose_model_classes.txt', 'r') as f:
        ret = f.read()
    ret = ret[1:len(ret) - 1]
    ret = ret.replace("\'", '')
    ret = ret.split()
    
    states = ret
    random.shuffle(states)
    print(states)
    return states


def shot(orda):
    ret = []
    ret.append(Button(400, 50, 20, 10, WHITE, str(orda), RED, fonts=48))

    for i, act in enumerate(orda):
        ret.append(Button(30 + i * 60, 100 + i * 00, 20, 10, WHITE, str(act), RED, fonts=36))
    return ret


def redo():
    screen.fill(WHITE)
    sel = False
    exi = Button(200, 250, 400, 100, WHITE, "Restart?", oc=RED)
    while not sel:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if exi.is_hover(mouse_pos) and exi.make:
                    exi.rem()
                    print("Restarting")
                    sel = True

        if exi.is_hover(mouse_pos):
            exi.color = HOVER
        else:
            exi.color = WHITE

        exi.draw(screen)
        pygame.display.flip()


def game(lev, dif):
    timeTo = 2 + dif * 2
    scom = 0.90 + (3 - dif) * 0.1
    ex = False

    order = leva(lev)
    last()
    count = 0
    ci = 0
    buts = []
    col = None
    match dif:
        case 3:
            col = GREEN
        case 2:
            col = GREEN
        case 1:
            col = GREEn
    while not ex:
        mouse_pos = pygame.mouse.get_pos()

        if count == 0:
            last()
            count += 1

        # scre,pos = retpos()
        # screen.blit(scre,(200,50))
        screen.fill(WHITE)

        if (ci == 0):
            buts = shot(order)
            buttonyy = Button(300, 250, 200, 50, WHITE, "Continue?", BLACK, 36, col)

            ci += 1
        for i in buts:
            i.draw(screen)
        if buttonyy.is_hover(mouse_pos):
            buttonyy.color = HOVER
        else:
            buttonyy.color = WHITE
        buttonyy.draw(screen)
        pygame.display.flip()
        if since() > timeTo:
            # ex = True
            pass
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ex = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttonyy.is_hover(mouse_pos) and buttonyy.make:
                    ex = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                ex = True
    escom = since()
    subt = 20 - escom * scom
    scom = round(subt/20,0)

    ex = False

    while not ex:
        screen.fill(WHITE)
        scre, pos = retpose()
        last()
        times = []
        comp = 0
        more = []
        back = Button(15, 15, swi / 1.95, swi * 4 / 10, WHITE, '', RED, fonts=24, oc=RED, round=False)
        for i in range(len(order)):
            more.append("?")
        cors = Button(670, 350, 100, 100, WHITE, '', RED, fonts=30, round=False)
        for act in order:
            top = "Finished:"
            for i in more:
                top += ("\n" + i)
            we = Button(675, 15, 100, 200, WHITE, top, RED, fonts=24, round=False)
            
            while pos != act:

                screen.fill(WHITE)
                back.draw(screen)
                frame, pos= retpose()
                shap = frame.shape
                frame=pygame.image.frombuffer(frame.tobytes(), frame.shape[1::-1], "BGR")
                high = Button(10, 10, shap[1] / 1.9175, shap[0] / 1.945, WHITE, '', oc=GREEN, fonts=24, round=False)
                high.draw(screen)
                
                screen.blit(frame, (10, 10))

                wel = Button(15, 483, 622, 100, WHITE, '', RED, fonts=24, oc=RED, round=False)
                welar = Button(30, 487.5, 200, 100, WHITE, (
                            "Current Move: " + str(pos) + "\n" + "\nPossible Score: " + str(
                        max(0, round(8 - since(), 3)))), RED, fonts=24, round=False)

                we.draw(screen, True)
                if since()>1.5:
                    cors.draw(screen,newt = '')
                else:
                    cors.draw(screen,newt = 'CORRECT!')
                wel.draw(screen)
                welar.draw(screen, True)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        ex = True
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                        ex = True
            more[comp] = act
            comp += 1
            cors.draw(screen,newt = "CORRECT!")
            pygame.display.flip()
            itim = last()
            if (itim < timeTo):
                times.append((act, round(8 - itim, 3), round(itim, 3)))
            else:
                times.append((act, 0, round(itim, 3)))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    ex = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    ex = True

        pygame.display.flip()
        for ac in times:
            print(ac, end=" ")
        ex = True
        # shot(order)
        toret = score(scom, times)

        return toret

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ex = True
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                ex = True

def endgame(psco):
    screen.fill(WHITE)
    while(since()<10):
        text = f"Final Score: {psco}"
        texer(screen,text,24,WHITE,200,400)

    
pose_thread = threading.Thread(target=retpose)
pose_thread.start()
swi = 1500
screen = pygame.display.set_mode((swi, swi * 3 / 5))
pygame.display.set_caption("Dance Game")


if __name__ == '__main__':
    

    model_name = 'level1_pose_model'
    

    with open(f'./danceOff/models/{model_name}.pkl', 'rb') as f:
        model = joblib.load(f)

    
    # Initiate holistic model

    
    while True:
        lev, dif = main_menu()
        print(dif)
        print(lev)
        psco = game(lev, dif)
        endgame(psco)
        redo()
                
        #if cv2.waitKey(1) & 0xFF == ord('q'):
                
               # break
    
    

