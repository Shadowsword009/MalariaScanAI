import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.efficientnet import preprocess_input as efficientnet_preprocess

# Ensure these match exactly what is in your static/Models folder
MODEL_PATHS = {
    0: './static/Models/Model EfficientNet.keras',
    1: './static/Models/Model DenseNet.keras',
    2: './static/Models/Model MobileNet.keras'
}

loaded_models = {}

def get_model(modelNo):
    if modelNo not in MODEL_PATHS:
        raise ValueError(f"Invalid model number received: {modelNo}")
        
    if modelNo not in loaded_models:
        model_path = MODEL_PATHS[modelNo]
        print(f"Loading Model {modelNo} from {model_path} into memory...")
        loaded_models[modelNo] = load_model(model_path)
        print(f"Model {modelNo} loaded successfully!")
        
    return loaded_models[modelNo]

def preprocess_image(image, modelNo):
    image = image.convert("RGB")
    image = image.resize((224, 224))
    image_array = img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)

    # Use proper preprocessing depending on model
    if modelNo == 0:
        # EfficientNet
        image_array = efficientnet_preprocess(image_array)
    else:
        # If others were trained using rescale=1./255
        image_array = image_array / 255.0

    return image_array

def predict(image, modelNo):
    model = get_model(modelNo)
    image_array = preprocess_image(image, modelNo)

    prediction = model.predict(image_array)

    print("Raw prediction:", prediction)

    return prediction