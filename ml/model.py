from .gbc.gbc import gbc_predict
from.cnn.cnn import cnn_predict


HIGH_RISK_MSG = "ALERT - Might be SQL Injection (HIGH risk)"
LOW_RISK_MSG = "ALERT - Might be SQL Injection (LOW risk)"
SAFE_MSG = "Seems to be safe"
OUTPUT_MSG = [SAFE_MSG, LOW_RISK_MSG, HIGH_RISK_MSG]


def predict_sqli(input):

    gbc_output = gbc_predict(input)
    cnn_output = cnn_predict(input)

    output_msg = OUTPUT_MSG[ gbc_output + cnn_output ]

    output = f"     input: { input }     ,     output: { output_msg }"

    return output
