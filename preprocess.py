
import cv2
import numpy as np
def find_receipt_corners(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # converting to grayscale black and white picture
    blurred=cv2.GaussianBlur(gray,(5,5),0) # blurring the image to slightly remove noise 5*5 represent kernal size small kernal less blur, big kernal more blur
    edges=cv2.Canny(blurred,80,200) # finding the edges in the image below 80 def not an edge above 200 def an edge, inb/w maybe
    kernal=np.ones((3,3),np.uint8)
    dilated=cv2.dilate(edges,kernal,iterations=1) # bridging the white pixel gaps so the shape could be completed if it is misscaned
    contours, _=cv2.findContours(dilated, # the input image
                                 cv2.RETR_LIST, # return list of all contours
                                 cv2.CHAIN_APPROX_SIMPLE # compressig contours to save memory a single edge line contains 100 of contour points this compress so that we get only the important ones. forexample if two points lies on the same line it discard one to save memory
                                 )
    contours=sorted(contours,key=cv2.contourArea,reverse=True # shape is closed
                    )[:5] # sorting the contours based on the shape area it covers and taking the top 5 contours
    debug_img=img.copy()
    cv2.drawContours(debug_img,contours,-1,(0,0,255),3) # all 5 in red
    cv2.imwrite("all top 5 .jpg",debug_img)
    cv2.imwrite("edges_debug.jpg", edges)
    for c in contours:
        perimeter=cv2.arcLength(c,
                                True)
        approx=cv2.approxPolyDP(c,
                               0.02*perimeter# 2% tollerence
                               ,True)# This tries to approximate the shapes with the tolerence if the distance from the point to the line is less than the tolerence it neglects the points
        if len(approx)==4: #simplifying the shape boundary points if the shape has 4 points than
            img_height,img_width,_=img.shape
            area_percentage= img_height*img_width# total area of the image
            if cv2.contourArea(c)/area_percentage>0.3: # if the quadrilateral is less than 30% of the area of the og photo discard it.
                return approx.reshape(4,2) # reshape the final format as 4 rows and 2 columns 2d array.
    return None #No 4 pts corners found.
def order_points(corners):
    rect=np.zeros((4,2),dtype="float32") # creating an array 0.0 intialized
    sums=[]
    for i in range(4):
        sums.append(corners[i][0]+corners[i][1])# this should take the sum of all items and give them in order
    rect[0]=corners[sums.index(min(sums))]# tl
    rect[2]=corners[sums.index(max(sums))]# br
    remaining=[]
    for i in range(4):
        if i!=sums.index(min(sums)) and i!= sums.index(max(sums)):
            remaining.append(corners[i])
    remainingdiff=[]
    for i in range(2):
        remainingdiff.append(remaining[i][0]-remaining[i][1])
    if remainingdiff[0] > remainingdiff[1]:
        rect[1]=remaining[0]
        rect[3]=remaining[1]
    else:
        rect[1]=remaining[1]
        rect[3]=remaining[0]

    return rect
def warp_receipt(img,corners):
    rect=order_points(corners)
    (tl,tr,br,bl)=rect
    #constructing a new angle cause the photo might be at an angle
    height=int(max(np.linalg.norm(tr-br),np.linalg.norm(tl-bl))) # getting the larger mag of the two heights
    width=int(max(np.linalg.norm(tr-tl),np.linalg.norm(br-bl)) )  # getting the larger mag of the two widths

    dst=np.array([[0,0]
                 ,[width-1,0]
                 ,[width-1,height-1],
                 [0,height-1]],dtype="float32") # we are gonna project the rectangle on these new coordinates
    M=cv2.getPerspectiveTransform(rect.astype("float32"),dst)# calculate the req tranformation to project
    warped=cv2.warpPerspective(img,M,(width,height)) # applies the new tranformation
    return warped

def binarize(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    threshold_value,threshold_img=cv2.threshold(gray,0,255,cv2.THRESH_BINARY +cv2.THRESH_OTSU)
    return threshold_img
def adaptive_binarize(img):
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)#converting to grayscale before handling uneven lighting
    threshold_img=cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,11)#different parts of the receipt can have different brightness
    return threshold_img
def upscale(img):
    return cv2.resize(img,None,fx=2,fy=2,interpolation=cv2.INTER_CUBIC)#making small receipt text larger for tesseract
def resize_for_ocr(img,max_dimension=1800):
    height,width=img.shape[:2]
    largest=max(height,width)
    if largest<=max_dimension:
        return img
    scale=max_dimension/largest
    return cv2.resize(img,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)#large phone images take much longer without improving receipt text
