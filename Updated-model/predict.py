import json


input_data = preprocess_image(image)
# Ensure correct dtype
if input_details[0]['dtype'] == np.uint8:
input_scale, input_zero_point = input_details[0]['quantization']
input_data = input_data / input_scale + input_zero_point
input_data = input_data.astype(np.uint8)


interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
output_data = interpreter.get_tensor(output_details[0]['index'])
# If output is logits, apply softmax
if output_details[0]['dtype'] in (np.float32, np.float64):
probs = tf.nn.softmax(output_data[0]).numpy()
else:
probs = output_data[0].astype(np.float32)
probs = probs / probs.sum()
return probs




def predict_with_keras(image: Image.Image):
model = tf.keras.models.load_model(KERAS_MODEL_PATH)
input_data = preprocess_image(image)
preds = model.predict(input_data)[0]
return preds




def predict_from_image(pil_image):
labels = load_labels()
num_labels = len(labels)
# Try TFLite first
try:
if os.path.exists(TFLITE_MODEL_PATH):
probs = predict_with_tflite(pil_image)
else:
raise FileNotFoundError
except Exception:
# fallback to Keras
probs = predict_with_keras(pil_image)


# Pair labels and probs
pairs = list(zip(labels, probs))
# Sort and return top-3
pairs_sorted = sorted(pairs, key=lambda x: x[1], reverse=True)
return pairs_sorted




if __name__ == '__main__':
# quick local test when running directly
from PIL import Image
img_path = 'tests/samples/sample.jpg'
if os.path.exists(img_path):
res = predict_from_image(Image.open(img_path))
print(res)
else:
print('No sample image found at', img_path)