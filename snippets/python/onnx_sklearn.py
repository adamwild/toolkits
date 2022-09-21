"""
python 3.10.6
scikit-learn==1.1.2
skl2onnx==1.12
onnxruntime==1.12.1

pip install sklearn skl2onnx onnxruntime
"""


import numpy as np
import onnxruntime as rt
import skl2onnx
from skl2onnx.common.data_types import FloatTensorType
from sklearn.datasets import load_iris
from sklearn.svm import OneClassSVM

numpy_type = np.float32
onnx_type = FloatTensorType

X, y = load_iris(return_X_y=True)
model = OneClassSVM(gamma="auto", kernel="linear", nu=0.01, tol=0.001)
model.fit(X.astype(numpy_type), y)

sklearn_scores = model.score_samples(X[:, :].astype(numpy_type))

# Convert into ONNX format
initial_type = [("input", onnx_type([None, X.shape[1]]))]
onx = skl2onnx.convert_sklearn(model, initial_types=initial_type)
with open("model.onnx", "wb") as f:
    f.write(onx.SerializeToString())

# Compute the prediction with ONNX Runtime
sess = rt.InferenceSession("model.onnx")

input_name = sess.get_inputs()[0].name
label_name = sess.get_outputs()[0].name
scores_name = sess.get_outputs()[1].name

pred_onx = sess.run([label_name, scores_name], {input_name: X[:, :].astype(numpy_type)})

onnx_score = pred_onx[1]

a = sklearn_scores - onnx_score.T[0]
m = a.mean()

breakpoint()
