import numpy as np
import cv2
import sys
import pygame
import time
import os

from imageio import imread

from code.button import *
from code.operations import *

time_ms = lambda: int(round(time.time() * 1000))

pygame.init()
pygame.display.set_caption("SSM_project")
clock = pygame.time.Clock() 

display = pygame.display.set_mode((1000,800))

display_surface_position = [300,20]

fps_text = Text(position=[305,25], size=[40,40], text="0", border=False, back=False, color_text=(255,255,255), text_size=30, font=None)

tracking_button_position = [30,20]
tracking_reset_button_position = [30,90]

global_button_position = [80,160]
local_button_position = [80,210]
dynamic_button_position = [80,260]

homography_button_position = [30,320]
homography_reset_button_position = [30,390]

image_button_position = [30,460]
live_button_position = [160,460]

image_selection_text = Text(position=[110,520], size=[40,40], text="Image selection (MAX 5)", border=False, back=False, color_text=(255,255,255), text_size=25, font=None)
#video_selection_text = Text(position=[600,520], size=[40,40], text="Video selection", border=False, back=False, color_text=(255,255,255), text_size=35, font=None)

image_browse_position = [30,570]
video_browse_position = [520,570]

camera_button_position = [520,520]
video_button_position = [650,520]
pause_button_position = [780,520]

camera_index_file = open("camera_index.txt", "r")
camera_index = int(camera_index_file.readlines()[0])
camera = cv2.VideoCapture(camera_index)


global_button = Button(position=global_button_position, size=[150,40], text="Global")
local_button = Button(position=local_button_position, size=[150,40], text="Local")
dynamic_button = Button(position=dynamic_button_position, size=[150,40], text="Dynamic")
global_button.state = 1

tracking_point_button = Button(position=tracking_button_position, size=[250,60], text="Add new tracking point")
tracking_point_reset_button = Button(position=tracking_reset_button_position, size=[250,60], text="Clear points")

homography_button = Button(position=homography_button_position, size=[250,60], text="Create homography")
homography_reset_button = Button(position=homography_reset_button_position, size=[250,60], text="Clear homography")

image_button = Button(position=image_button_position, size=[120,40], text="Image")
image_button.state = 1
live_button = Button(position=live_button_position, size=[120,40], text="Live")

camera_button = Button(position=camera_button_position, size=[120,40], text="Camera")
camera_button.state = 1
video_button = Button(position=video_button_position, size=[120,40], text="Video")

pause_button = Button(position=pause_button_position, size=[120,40], text="Pause")

text_area = TextArea()

button_list = []
button_list.append(global_button)
button_list.append(local_button)
button_list.append(dynamic_button)
button_list.append(tracking_point_button)
button_list.append(tracking_point_reset_button)
button_list.append(homography_button)
button_list.append(homography_reset_button)
button_list.append(image_button)
button_list.append(live_button)
button_list.append(camera_button)
button_list.append(video_button)
button_list.append(pause_button)

##

image_list = []
images = os.listdir("./images/")

temp_images = []
for count, image in enumerate(images):
    if count == 5:
        break
    temp_images.append(image)
images = temp_images

#images = images[:max(len(images),5)]

for count, image in enumerate(images):
    b_image = Button(position=[35,575 + count * 35], size=[390,40], text=image, border=False)
    image_list.append(b_image)

image_select = imread("./images/{}".format(images[0]))
image_select = np.rot90(image_select)
image_list[0].state = 1

##

video_list = []
videos = os.listdir("./videos/")

temp_videos = []
for count, video in enumerate(videos):
    if count == 5:
        break
    temp_videos.append(video)
videos = temp_videos

#videos = videos[:max(len(videos),5)]

for count, video in enumerate(videos):
    b_image = Button(position=[525,575 + count * 35], size=[390,40], text=video, border=False)
    video_list.append(b_image)

prev_image = None
dynamic_count = 0

tracking_point = []
tracking_kernel = []

tracking_kernel_dyn = []
tracking_point_dyn = []

homography_point = []
homography_kernel = []

homography_kernel_dyn = []
homography_point_dyn = []

kernel_size = 20
local_area_size = 50

video_load = None

fps = 0
running = True
while running:

    clock.tick(30) #FORCE MAX FPS
    fps_text.change_text(int(clock.get_fps())+1)

    if pause_button.state == 0:
        if camera_button.state == 1:
            _, camera_frame = camera.read() 
            camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
            camera_frame = np.rot90(camera_frame)
        else:
            if video_load is not None:
                _, camera_frame = video_load.read()    
                if not _:
                    video_load = cv2.VideoCapture("./videos/{}".format(video.text))  
                    _, camera_frame = video_load.read()  
                camera_frame = cv2.resize(camera_frame, (640,480), interpolation = cv2.INTER_AREA)
                camera_frame = np.rot90(camera_frame)
                camera_frame = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
                camera_frame = camera_frame
            
    for event in pygame.event.get():   
        if event.type == pygame.QUIT:
            running = False   

    dynamic_count += 1
    if dynamic_count > max(len(tracking_point), len(homography_point)):
        dynamic_count = 0
        
    ### TRACKING POINTS
    
    # POINTS
    remove_point_list = []
    for count, point in enumerate(tracking_point):    
        prev_point = point.copy() 
        
        if valid(camera_frame, point, local_area_size): 
            if global_button.state == 1:
                point[0], point[1] = track_point_global(point, camera_frame, tracking_kernel[count], kernel_size)
            elif local_button.state == 1:
                point[0], point[1] = track_point_local(point, camera_frame, tracking_kernel[count], local_area_size)
            elif dynamic_button.state == 1:
                if count == dynamic_count:
                    point[0], point[1] = track_point_global(point, camera_frame, tracking_kernel[count], kernel_size)
                else:
                    point[0], point[1] = track_point_local(point, camera_frame, tracking_kernel[count], local_area_size)
        else:
            remove_point_list.append(count)
        
        if valid(camera_frame, tracking_point_dyn[count], local_area_size): 
            tracking_point_dyn[count][0], tracking_point_dyn[count][1] = track_point_local(tracking_point_dyn[count], camera_frame, tracking_kernel_dyn[count], local_area_size)
        else:
            remove_point_list.append(count)
            
        # DYN+STATIC
        prev_static_point = np.array(prev_point)
        static_point = np.array(point)
        dyn_point = np.array(tracking_point_dyn[count])
        
        dist = np.linalg.norm(dyn_point-static_point)
        
        if dist < 25:
            tracking_point_dyn[count] = point.copy()
            
        dist = np.linalg.norm(prev_static_point-static_point)
        
        if dist > 25:
            point = tracking_point_dyn[count].copy()       
            
        point = tracking_point_dyn[count]
        tracking_kernel_dyn[count] = camera_frame[point[0]-kernel_size:point[0]+kernel_size, point[1]-kernel_size:point[1]+kernel_size, :]                 

    remove_point_list.reverse()
    for point in remove_point_list:
        tracking_point.pop(point)
        tracking_kernel.pop(point)
        
        tracking_kernel_dyn.pop(point)
        tracking_point_dyn.pop(point)
    
    # HOMOGRAPHY POINTS
    remove_point_list = []
    for count, point in enumerate(homography_point):    
        prev_point = point.copy()
      
        if valid(camera_frame, point, local_area_size): 
            if global_button.state == 1:
                point[0], point[1] = track_point_global(point, camera_frame, homography_kernel[count], kernel_size)
            elif local_button.state == 1:
                point[0], point[1] = track_point_local(point, camera_frame, homography_kernel[count], local_area_size)
            elif dynamic_button.state == 1:
                if count == dynamic_count:
                    point[0], point[1] = track_point_global(point, camera_frame, homography_kernel[count], kernel_size)
                else:
                    point[0], point[1] = track_point_local(point, camera_frame, homography_kernel[count], local_area_size)
        else:
            remove_point_list.append(count)

        if valid(camera_frame, homography_point_dyn[count], local_area_size): 
            homography_point_dyn[count][0], homography_point_dyn[count][1] = track_point_local(homography_point_dyn[count], camera_frame, homography_kernel_dyn[count], local_area_size)
        else:
            remove_point_list.append(count)
            
        # DYN+STATIC
        prev_static_point = np.array(prev_point)
        static_point = np.array(point)
        dyn_point = np.array(homography_point_dyn[count])
        
        dist = np.linalg.norm(dyn_point-static_point)
        
        if dist < 35:
            homography_point_dyn[count] = point.copy()
            
        dist = np.linalg.norm(prev_static_point-static_point)
        
        if dist > 25:
            point = homography_point_dyn[count].copy()       
            
        point = homography_point_dyn[count]
        homography_kernel_dyn[count] = camera_frame[point[0]-kernel_size:point[0]+kernel_size, point[1]-kernel_size:point[1]+kernel_size, :] 

    remove_point_list.reverse()
    for point in remove_point_list:
        homography_point.pop(point)
        homography_kernel.pop(point)

        homography_kernel_dyn.pop(point)
        homography_point_dyn.pop(point)
    
    # HOMOGRAPHY

    if len(homography_point) == 4:
        point_0 = homography_point[0][::-1]
        point_1 = homography_point[1][::-1]
        point_2 = homography_point[2][::-1]
        point_3 = homography_point[3][::-1]
        point_destination = np.array([point_0, point_1, point_2, point_3])     
        
        if live_button.state == 1:
            image_projection = np.flip(prev_image, axis=0)
            image_projection_points = point_source = np.array([[0, 0], [image_projection.shape[1], 0], [image_projection.shape[1], image_projection.shape[0]], [0, image_projection.shape[0]]])
        else:
            image_projection = image_select
            image_projection_points = point_source = np.array([[0, 0], [image_projection.shape[1], 0], [image_projection.shape[1], image_projection.shape[0]], [0, image_projection.shape[0]]])        

        H, status = cv2.findHomography(image_projection_points, point_destination, cv2.RANSAC, 5.0)        
        out = cv2.warpPerspective(image_projection, H, (480, 640))

        mask = (out == 0)
        temp = np.all(mask, axis=2)
        mask[:,:,0] = temp
        mask[:,:,1] = temp
        mask[:,:,2] = temp
        
        new_array = np.copy(out)
        new_array[mask] = camera_frame[mask]
    else:
        new_array = camera_frame.copy()
 
    # ADD POINT

    if tracking_point_button.click():
        tracking_point_button.state = (tracking_point_button.state + 1) % 2

    if tracking_point_button.state == 1:  
        if tracking_point_button.click_time + 100 < time_ms():
            if pygame.mouse.get_pressed()[0]:
                tracking_point_button.click_time = time_ms()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                if mouse_x - display_surface_position[0] >= 0 and mouse_x - display_surface_position[0] < camera_frame.shape[0]:
                    if mouse_y - display_surface_position[1] >= 0 and mouse_y - display_surface_position[1] < camera_frame.shape[1]:
                    
                        point = [mouse_x - display_surface_position[0], mouse_y - display_surface_position[1]]
                        
                        if valid(camera_frame, point, kernel_size):
                            kernel = camera_frame[point[0]-kernel_size:point[0]+kernel_size, point[1]-kernel_size:point[1]+kernel_size, :]
                        
                            tracking_point.append(point.copy())                 
                            tracking_kernel.append(kernel.copy())
                            
                            tracking_point_dyn.append(point.copy())   
                            tracking_kernel_dyn.append(kernel.copy())
                            
                            tracking_point_button.state = 0

    # ADD HOMOGRAPHY
        
    if homography_button.click():
        homography_button.state = (homography_button.state + 1) % 2                    
        
    if homography_button.state == 1:  
        if homography_button.click_time + 100 < time_ms():
            if pygame.mouse.get_pressed()[0]:
                homography_button.click_time = time_ms()
                mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                if mouse_x - display_surface_position[0] >= 0 and mouse_x - display_surface_position[0] < camera_frame.shape[0]:
                    if mouse_y - display_surface_position[1] >= 0 and mouse_y - display_surface_position[1] < camera_frame.shape[1]:
                    
                        point = [mouse_x - display_surface_position[0], mouse_y - display_surface_position[1]]
                        
                        if valid(camera_frame, point, kernel_size):
                            kernel = camera_frame[point[0]-kernel_size:point[0]+kernel_size, point[1]-kernel_size:point[1]+kernel_size, :]
                        
                            homography_point.append(point.copy())                 
                            homography_kernel.append(kernel.copy()) 

                            homography_point_dyn.append(point.copy())   
                            homography_kernel_dyn.append(kernel.copy())
                            
                            if len(homography_point) == 4:
                                homography_button.state = 0

    

    # GLOBAL/LOCAL/DYNAMIC
    if global_button.hover():
        if pygame.mouse.get_pressed()[0]:
            global_button.state = 1
            local_button.state = 0
            dynamic_button.state = 0
                
    if local_button.hover():
        if pygame.mouse.get_pressed()[0]:
            global_button.state = 0
            local_button.state = 1
            dynamic_button.state = 0

    if dynamic_button.hover():
        if pygame.mouse.get_pressed()[0]:
            local_button.state = 0
            global_button.state = 0
            dynamic_button.state = 1
                
    # TRACKING POINTS RESET
    if tracking_point_reset_button.click():
        tracking_point = []
        tracking_kernel = []
        
        tracking_kernel_dyn = []
        tracking_point_dyn = []       

    if homography_reset_button.click():
        homography_point = []
        homography_kernel = []
        
        homography_kernel_dyn = []
        homography_point_dyn = []

    # IMAGE/LIVE
    if image_button.click():
        image_button.state = 1
        live_button.state = 0
    
    if live_button.click():
        image_button.state = 0
        live_button.state = 1

    # CAMERA/VIDEO
    if camera_button.click():
        camera_button.state = 1
        video_button.state = 0
    
    if video_button.click():
        camera_button.state = 0
        video_button.state = 1
   
    # PAUSE
    if pause_button.click():
        pause_button.state = (pause_button.state + 1) % 2
   
    # IMAGE SELECT 
    
    for count, image in enumerate(image_list):
        if image.state != 1:
            if image.click():
                image_select = imread("./images/{}".format(image.text))
                image_select = np.rot90(image_select)
                
                for image_2 in image_list:
                    image_2.state = 0
                image.state = 1

    # VIDEO SELECT 
    
    for count, video in enumerate(video_list):
        if video.state != 1:
            if video.click():
                video_load = cv2.VideoCapture("./videos/{}".format(video.text))               
                for video_2 in video_list:
                    video_2.state = 0
                video.state = 1
    
    # DISPLAY
            
    prev_image = new_array
    display_surface = pygame.surfarray.make_surface(new_array)
    
    for point in tracking_point_dyn:
        pygame.draw.circle(display_surface, (255,0,0), point, 5)
    
    #for point in tracking_point:
    #    pygame.draw.circle(display_surface, (255,0,0), point, 5)

    for point in homography_point:
        pygame.draw.circle(display_surface, (0,255,0), point, 5)
 
    display.blit(display_surface, display_surface_position)  
    fps_text.display(display)
    image_selection_text.display(display)
    #video_selection_text.display(display)
    
    for button in button_list:  
        button.display(display)

    # IMAGE AREA
    text_area.display(display, image_browse_position, [400,200])

    # VIDEO AREA
    text_area.display(display, video_browse_position, [400,200])
    
    for image in image_list:
        image.display(display)

    for video in video_list:
        video.display(display)
    
    pygame.display.update()

pygame.quit()
camera.release()
cv2.destroyAllWindows()