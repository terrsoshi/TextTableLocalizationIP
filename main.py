# -*- coding: utf-8 -*-

#Importing all the required modules
import cv2
import sys
import glob
import subprocess
import numpy as np
from matplotlib import pyplot as pt

#If the module pdf2jpg has not been imported before in the user's current session, the package pdf2jpg will be installed using pip. If not, only pdf2jpg function from pdf2jpg module will be imported
if 'pdf2jpg' in sys.modules: 
    from pdf2jpg import pdf2jpg
else:
    subprocess.call(['pip', 'install', 'pdf2jpg'])
    from pdf2jpg import pdf2jpg

#Main Menu
while True: #Loops the user back to the Main Menu if there is any error.
    try: 
        exits=False 
        #Our program has three different selecting image options along with one exit option
        print("\n<--MAIN MENU-->")
        print("\n1. Convert PDF documents into images\n2. Select a folder containing images (Only JPG and PNG images)\n3. Select image(s)\n4. Exit program\n")
        mode=int(input(""))
            
        if mode==1: #Convert PDF documents into images in JPG format
            try:
                #Prompts user to enter full path of pdf document to be converted into image and processed.
                userpdf=input("Please enter the full path of the pdf document \n(Eg. "+r"C:\Users\Eugene\Desktop\CSC2014 Assignment Aug 2019\Test Files\Test PDF Documents\test.pdf) :"+"\n\n")
                sourcepath = r""+userpdf
                
                #Prompts user to enter full path of the destination folder for the converted images to be saved into.
                userfolder=input("Please enter the full path of the folder for images to be saved to \n(Eg. "+r"C:\Users\Eugene\Desktop\CSC2014 Assignment Aug 2019\Test Files\Test PDF Documents) :"+"\n\n")
                destinationpath = r""+userfolder
                
                #Convert all pages of user's pdf into separate images saved in jpg format.
                convert = pdf2jpg.convert_pdf2jpg(sourcepath, destinationpath, pages="ALL")
                
                #If the entered pdf document cannot be found, output_jpgfiles list in dictionary at index 0 of convert list will be empty. An exception is raised if this happens.
                if len(convert[0]['output_jpgfiles'])==0:
                    raise Exception
                    
                #Get the pdf file name from user's first input
                pdfsplit=sourcepath.split("\\")
                pdfname=pdfsplit[len(pdfsplit)-1]
                
                #Read all converted images in jpg format in the destination folder and save all of it into the pages list
                pages = [cv2.imread(image) for image in glob.glob(r""+destinationpath+"\\"+pdfname+"_dir\\*.jpg")]
                break #Break out of the loop and move on to processing the images if there is no error.
            
            #If the PDF document entered cannot be found
            except Exception:
                print("\nPDF document cannot be found!")
                
        elif mode==2: #Select a folder containing images
            #Prompts user to enter full path of the folder containing images, only JPG and PNG images will be read.
            userfolder=input("Please enter the full path of the folder containing images (Only JPG and PNG images) \n(Eg. "+r"C:\Users\Eugene\Desktop\CSC2014 Assignment Aug 2019\Test Files\Test Images) :"+"\n\n")
            
            #Read all the images in JPG and PNG format in the entered folder and save all of it into the pages list
            pages = [cv2.imread(image) for image in glob.glob(r""+userfolder+"\\*.jpg")]
            images_png=[cv2.imread(image) for image in glob.glob(r""+userfolder+"\\*.png")]
            for image in images_png:
                pages.append(image)
                
            #If the entered folder is empty or does not exist, pages list will be empty. When this happens, user will be brought back to the main menu.
            if len(pages) == 0:
                print("\nThe entered folder is empty or does not exist.")
            #Else, break out of the loop and move on to processing the images
            else: 
                break
                
        elif mode==3: #Select image(s)
            try:
                pages=[] #Initialise pages list
                #Prompts user to enter number of images to process
                noofimages=int(input("Please enter the number of images to process: "))
                
                #Loop according to the number of images to process
                for i in range(noofimages):
                    #Prompts user to enter full path of image to be read
                    userimage=input("Please enter the full path of image "+str(i+1)+" \n(Eg. "+r"C:\Users\Eugene\Desktop\CSC2014 Assignment Aug 2019\Test Files\Test Images\test_1.jpg) :"+"\n\n")
                    image=cv2.imread(r""+userimage, 1)
                    
                    #If the image exists and can be read, append into the pages list
                    if image.size!=0:
                        pages.append(image)
                    #If the image file does not exist and cannot be read, an exception is raised.
                    else:
                        raise Exception
                break #Break out of the loop and move on to processing the images if there is no error.   
                
            except ValueError: #Ensure user key in a valid number
                print("\nYou have entered an invalid input, please enter a valid number.")    
                
            except Exception: #If the image file does not exist and cannot be read
                print("\nThe image entered does not exist.")
    
                
        elif mode==4: #Exit Program
            exits=True #Sets exits to True to skip for page in pages loop and end the program.
            break 
            
        else: #Ensure user enters a number between 1-4
            print("\nYou have entered an invalid number, please enter again.")
            
    except ValueError: #Ensure user key in a valid number
            print("\nYou have entered an invalid input, please enter a valid number.")

#Process each image(page of the pdf) in the list
if exits==False:
    print("\nThe images are being processed right now, please wait...\n")
    for page in pages:
        #Convert colour image from BGR format to RGB format to show the correct colours in the end using pt.imshow()
        page_rgb=cv2.cvtColor(page,cv2.COLOR_BGR2RGB)
        
        #Convert image into grayscale to process
        page_grayscale=cv2.cvtColor(page_rgb,cv2.COLOR_RGB2GRAY)
        
        #Get shape of the image to create a binary image
        [nrow,ncol]=page_grayscale.shape
        bin_page=np.zeros((nrow,ncol),dtype=np.uint8)
    
        #Apply thresholding to invert the blacks and whites of the image in the binary image.
        #Because in OpenCV, finding contours is like finding white objects from black background.
        threshold=245
        for x in range(0, nrow):
            for y in range(0, ncol):
                if page_grayscale[x,y]<=threshold:
                    bin_page[x,y]=255
        
        #Create a 6x13 rectangularstructuring element
        sE_dilate=cv2.getStructuringElement(cv2.MORPH_RECT, (13,6))
        #Applying 4 iterations of dilation to the binary image to join the texts together using the structuring element
        #Structuring element is symmetrical, therefore no rotation is needed to apply on structuring element.
        bin_dilated= cv2.dilate(bin_page, sE_dilate, iterations=4) 
    
        #Find contours of text areas and tables (whites) from dilated binary image
        #Try and except for different versions of OpenCV
        try: #For all versions of OpenCV besides version 3.x
            contours, hierarchy = cv2.findContours(bin_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except Exception: #For OpenCV version 3.x
            modified_page, contours, hierarchy = cv2.findContours(bin_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)    
            
        #Fill up cells inside contour of tables with whites to exclude texts inside the tables
        for contour in contours:
            cv2.drawContours(bin_dilated, [contour], 0, (255,255,255), -1)
            
        #Reset total contours list with new list of contours excluding texts and gaps inside tables  
        #Try and except for different versions of OpenCV
        try: #For all versions of OpenCV besides version 3.x
            contours, hierarchy = cv2.findContours(bin_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except Exception: #For OpenCV version 3.x
            modified_page, contours, hierarchy = cv2.findContours(bin_dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)    
        
    
        #Process each contour in total contours list        
        for contour in contours:
            #Find coordinates, width, and height of each contour
            (col,row,width,height)=cv2.boundingRect(contour)
            
            #Initialise number of black pixels in contours to 0 in each loop
            noofblack=0
            
            #Process each pixel in the contour
            for nrow in range (row, row+height):
                for ncol in range (col, col+width):
                    
                    #If a black pixel is found, increase the number of black pixels in contours by one
                    if bin_dilated[nrow,ncol] == 0:
                        noofblack+=1
                        
            #If the total number of black pixels in the contour is more than 1 percent of the contour, it is assumed that the contour contains only texts            
            if noofblack > (1/100)*(width*height):
                #A Blue rectangle is drawn for text contours
                cv2.rectangle(page_rgb, (col, row), (col+width, row+height), (0, 0, 255), 4)
            
            #Else, if the total number of black pixels in the contour is less than 1 percent of the contour, it is assumed that the contour contains a table
            else:
                #A Red rectangle is drawn for table contours
                cv2.rectangle(page_rgb, (col, row), (col+width, row+height), (255, 0, 0), 4)
    
        
        #The output image of each page with texts and tables located is shown in separate figures
        pt.figure()
        pt.imshow(page_rgb)
        pt.show()

print("\nTexts are highlighted in blue boxes, Tables are highlighted in red boxes.") #labellings to differentiate texts and tables
print("\nThanks for using our program, have a nice day!") #Goodbye message
