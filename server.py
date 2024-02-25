import os
from flask import Flask, request, Response, g, render_template, jsonify
import google.generativeai as genai
import json

from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

app = Flask(__name__)
app.debug = True

model = genai.GenerativeModel(model_name="gemini-pro-vision")

@app.route('/', methods=['GET'])
def hello_world():
    return render_template("chat.html")

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_image' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['user_image']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        image_data = file.read()
        image_parts = [
            {
                "mime_type": file.content_type,
                "data": image_data
            },
        ]

        prompt_parts = [
            """
            You are an expert in understanding invoices.
            You will receive a single input image as invoice &
            you will have to convert the invoice image into JSON format. 
            If the image is not recognized as invoice, respond with black JSON object with the template format.
            Use the following key format for the response:
            {
                store_name: 'name_of_the_store',
                subtotal: 'total_invoice_amount',
                tax: 'tax_in_the_receipt',    
                invoice_date: "date_printed_on_invoice"
                invoice_number: "invoice_unique_id",
                invoice_time: "time_printed_on_invoice",
                items:[
                    {
                        id: 'number_in_the_list',
                        item_name: 'example_name',
                        total: 'amount'
                    }
                ]
            }
            If any field is not found, leave it as blank.
            DO NOT include anything else other than the JSON, including any variable name. Also do not include 'json' at the start of the response.
            Do not include any string formatting.
            Wrap the answer in triple quotes (") to use in python and not in ticks (`).
            """,
            image_parts[0]
        ]  


        response = model.generate_content(prompt_parts)
        print(response.text)
        res = json.loads(response.text)
        return res
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))