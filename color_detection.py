import pandas as pd
import cv2
import pyttsx3   # For text-to-speech
import threading

# ========== Setup ==========
imageUrl = 'Colour-Detection-System/Best-Things-to-Do-in-New-York-City-at-Night.jpg'
clicked = False
redValue = 0
greenValue = 0
blueValue = 0
xPosition = 0
yPosition = 0

# Initialize pyttsx3 engine
engine = pyttsx3.init()
engine.setProperty('rate', 110)      
engine.setProperty('volume', 1.0)   

# Load CSV
colorNameDataFrame = pd.read_csv('Colour-Detection-System/wikipedia_color_names.csv')
colorNameDataFrame.drop(colorNameDataFrame.iloc[:, 5:8], inplace=True, axis=1)
colorNameDataFrame.rename(columns={
    'Hex (24 bit)': 'Hex',
    'Red (8 bit)': 'Red',
    'Green (8 bit)': 'Green',
    'Blue (8 bit)': 'Blue'
}, inplace=True)

# Load image
image = cv2.imread(imageUrl)


# ========== Functions ==========
def getColorName(red, green, blue):
    minimumValue = 10000
    colorName = "Unknown"
    for i in range(len(colorNameDataFrame)):
        rgbValue = abs(red - int(colorNameDataFrame.loc[i, "Red"])) + \
                   abs(green - int(colorNameDataFrame.loc[i, "Green"])) + \
                   abs(blue - int(colorNameDataFrame.loc[i, "Blue"]))
        if rgbValue <= minimumValue:
            minimumValue = rgbValue
            colorName = colorNameDataFrame.loc[i, "Name"]
    return colorName


def speakColorName(name):
    try:
        # Ensure any previous speech is stopped before starting new one
        engine.stop()
        engine.say(str(name))
        engine.runAndWait()
    except Exception:
        # Fallback: re-init engine and try once more
        fallback_engine = pyttsx3.init()
    fallback_engine.setProperty('rate', 110)
    fallback_engine.setProperty('volume', 1.0)
    fallback_engine.say(str(name))
    fallback_engine.runAndWait()

# Helper to run speech in a thread
def speakColorNameThreaded(name):
    threading.Thread(target=speakColorName, args=(name,), daemon=True).start()


def draw_function(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global blueValue, greenValue, redValue, xPosition, yPosition, clicked
        clicked = True
        xPosition = x
        yPosition = y
        blueValue, greenValue, redValue = image[yPosition, xPosition]
        blueValue = int(blueValue)
        greenValue = int(greenValue)
        redValue = int(redValue)


# ========== Main ==========
if __name__ == '__main__':
    cv2.namedWindow('Color Name')
    cv2.setMouseCallback('Color Name', draw_function)

    # Keep a copy of the original image
    original_image = image.copy()

    # State to remember last color and name
    last_color = None
    last_text = None
    last_bgr = (0, 0, 0)

    while True:
        # Always start with a fresh copy for each frame
        display_image = original_image.copy()

        if clicked:
            # Get nearest color name
            colorName = getColorName(redValue, greenValue, blueValue)
            text = f"Selected color name is: {colorName}"
            last_color = (blueValue, greenValue, redValue)
            last_text = text
            last_bgr = (redValue, greenValue, blueValue)
            # 🔊 Speak color name every click (in a thread)
            speakColorNameThreaded(colorName)
            clicked = False

        # Draw the last selected color and name if available
        if last_color and last_text:
            cv2.rectangle(display_image, (20, 20), (950, 60), last_color, -1)
            # Put text on image
            cv2.putText(display_image, last_text, (50, 50), 2, 0.75, (255, 255, 255), 1, cv2.FONT_ITALIC)
            # Adjust text color if background is too bright
            brightness = sum(last_bgr)
            if brightness >= 600:
                cv2.putText(display_image, last_text, (50, 50), 2, 0.75, (0, 0, 0), 1, cv2.FONT_ITALIC)

        # Show window
        cv2.imshow("Color Name", display_image)

        # Break loop on ESC key
        if cv2.waitKey(20) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
