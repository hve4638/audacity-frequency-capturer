import cv2
import pytesseract
from PIL import Image

# Load the image
img = cv2.imread('D:\\Workspace\\python\\frequencycapture\\.tmp\\240510104941pfap.png')

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply thresholding to segment the text
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Write the thresholded image to disk
cv2.imwrite('thresh.jpg', thresh)

# Use Tesseract-OCR to extract the text
text = pytesseract.image_to_string(Image.open('thresh.jpg'))

# Print the extracted text
print(text)