import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import json

from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

app = Flask(__name__)
app.debug = True

cors = CORS(app)

model = genai.GenerativeModel(model_name="gemini-pro-vision")
model_text = genai.GenerativeModel(model_name="gemini-pro")

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello from paisa"})

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
            you will have to convert the invoice image into valid JSON format. 
            If the image is not recognized as invoice, respond with blank JSON object with the template format.
            Use the following key format for the response:
            {
                store_name: 'name_of_the_store',
                store_address: 'address_of_the_store',
                subtotal: 'total_invoice_amount_including_tax',
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
            If any field is not found, leave it as blank. Do not add tax, balance, savings in items. Do not invent any items.
            DO NOT include anything else other than the JSON, including any variable name and extra white spaces. Also do not include 'json' at the start of the response.
            Do not include any string formatting.
            Wrap the answer in triple quotes (") to use in python and not in ticks (`).
            """,
            image_parts[0]
        ]  

        # json_prompt = """ 
        #     The following response was not parsed as a JSON object. Reformat the response in JSON format.
        #     Use the following key format for the JSON object:
        #     {
        #         store_name: 'name_of_the_store',
        #         store_address: 'address_of_the_store',
        #         subtotal: 'total_invoice_amount_including_tax',
        #         tax: 'tax_in_the_receipt',    
        #         invoice_date: "date_printed_on_invoice"
        #         invoice_number: "invoice_unique_id",
        #         invoice_time: "time_printed_on_invoice",
        #         items:[
        #             {
        #                 id: 'number_in_the_list',
        #                 item_name: 'example_name',
        #                 total: 'amount'
        #             }
        #         ]
        #     }
        #     Modify the following JSON:
        # """

        response = model.generate_content(prompt_parts)
        print(response.text)
        try:
            res = json.loads(response.text.strip())
        except ValueError as e:
            return jsonify({"error": "Could not read the image"})
        return res
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))