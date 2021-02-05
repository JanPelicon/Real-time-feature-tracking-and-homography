import cv2
import numpy as np

def valid(source, point, size):
    width = source.shape[0]
    height = source.shape[1]
    
    if point[0] - size < 0:
        return False
    if point[1] - size < 0:
        return False
    if point[0] + size >= width:
        return False
    if point[1] + size >= height:
        return False
        
    return True  
    
def track_point_local(point, camera_frame, kernel, area_size):
    source = camera_frame[point[0]-area_size:point[0]+area_size, point[1]-area_size:point[1]+area_size, :]#.copy()
             
    source_0 = source[:,:,0]
    source_1 = source[:,:,1]
    source_2 = source[:,:,2] 
               
    kernel_0 = kernel[:,:,0]
    kernel_1 = kernel[:,:,1]
    kernel_2 = kernel[:,:,2]

    correlation_0 = cv2.matchTemplate(source_0, kernel_0, cv2.TM_CCOEFF_NORMED)
    correlation_1 = cv2.matchTemplate(source_1, kernel_1, cv2.TM_CCOEFF_NORMED)
    correlation_2 = cv2.matchTemplate(source_2, kernel_2, cv2.TM_CCOEFF_NORMED)
    
    x_0, y_0  = np.unravel_index(correlation_0.argmax(), correlation_0.shape)
    x_1, y_1  = np.unravel_index(correlation_1.argmax(), correlation_1.shape)
    x_2, y_2  = np.unravel_index(correlation_2.argmax(), correlation_2.shape)
    location = ((x_0 + x_1 + x_2)//3, (y_0 + y_1 + y_2)//3)            

    #cv2.imshow("N", cv2.resize(source_0, (400,400)))
    
    argmax_sum = (correlation_0.argmax() + correlation_1.argmax() + correlation_2.argmax()) / 3

    x = point[0] + location[0] - correlation_0.shape[0]//2
    y = point[1] + location[1] - correlation_0.shape[1]//2  
    
    return x,y
    
def track_point_global(point, camera_frame, kernel, kernel_size):
    source = camera_frame#.copy()
             
    source_0 = source[:,:,0]
    source_1 = source[:,:,1]
    source_2 = source[:,:,2] 
               
    kernel_0 = kernel[:,:,0]
    kernel_1 = kernel[:,:,1]
    kernel_2 = kernel[:,:,2]

    correlation_0 = cv2.matchTemplate(source_0, kernel_0, cv2.TM_CCOEFF_NORMED)
    correlation_1 = cv2.matchTemplate(source_1, kernel_1, cv2.TM_CCOEFF_NORMED)
    correlation_2 = cv2.matchTemplate(source_2, kernel_2, cv2.TM_CCOEFF_NORMED)

    distance_matrix = np.ndarray((640-2*kernel_size+1,480-2*kernel_size+1))
    distance_matrix.fill(0.70)
    
    translated_point = np.array(
        [point[0] - int(kernel.shape[0]/2),
        point[1] - int(kernel.shape[1]/2)]
        )
    
    x_low = max(translated_point[0]-2*kernel_size, 0)
    x_high = min(translated_point[0]+2*kernel_size, distance_matrix.shape[0])
    
    y_low = max(translated_point[1]-2*kernel_size, 0)
    y_high = min(translated_point[1]+2*kernel_size, distance_matrix.shape[0])
    
    distance_matrix[x_low:x_high, y_low:y_high] = 0.85
    distance_matrix[translated_point[0]-kernel_size:translated_point[0]+kernel_size, translated_point[1]-kernel_size:translated_point[1]+kernel_size] = 1
    
    correlation_0 = np.multiply(correlation_0, distance_matrix)
    correlation_1 = np.multiply(correlation_1, distance_matrix)
    correlation_2 = np.multiply(correlation_2, distance_matrix)
    
    x_0, y_0  = np.unravel_index(correlation_0.argmax(), correlation_0.shape)
    x_1, y_1  = np.unravel_index(correlation_1.argmax(), correlation_1.shape)
    x_2, y_2  = np.unravel_index(correlation_2.argmax(), correlation_2.shape)

    location = ((x_0 + x_1 + x_2)//3, (y_0 + y_1 + y_2)//3)            
    
    argmax_sum = (correlation_0.argmax() + correlation_1.argmax() + correlation_2.argmax()) / 3

    x = location[0] + int(kernel.shape[0]/2)
    y = location[1] + int(kernel.shape[1]/2)
    
    return x,y