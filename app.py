from flask import Flask, request, render_template, jsonify
from encryption import generate_private_key, generate_public_key, compute_shared_secret, encrypt_message, decrypt_message
import boto3
import uuid

# Initialize S3 client
s3 = boto3.client('s3', region_name='ap-south-1')
BUCKET_NAME = 'cclpro1'  # replace with your bucket name

def store_encrypted_message_s3(encrypted_message):
    message_id = str(uuid.uuid4())
    object_key = f"{message_id}.txt"
    s3.put_object(Bucket=BUCKET_NAME, Key=object_key, Body=encrypted_message.encode())
    return message_id

def retrieve_encrypted_message_s3(message_id):
    object_key = f"{message_id}.txt"
    response = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
    encrypted_message = response['Body'].read().decode()
    return encrypted_message

app = Flask(__name__)

@app.route('/')
def home():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        messages = []

        for obj in response.get('Contents', []):
            object_key = obj['Key']
            file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
            encrypted_text = file_obj['Body'].read().decode()
            messages.append(encrypted_text)

        return render_template('index.html', messages=messages)

    except Exception as e:
        return jsonify({"error": str(e)})



@app.route('/generate_keys', methods=['GET'])
def generate_keys():
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    return jsonify({"private_key": private_key, "public_key": public_key})

@app.route('/compute_secret', methods=['POST'])
def compute_secret():
    data = request.json
    private_key = int(data['private_key'])
    received_public_key = int(data['received_public_key'])
    shared_secret = compute_shared_secret(private_key, received_public_key)
    return jsonify({"shared_secret": shared_secret})

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.get_json(force=True)
    message = data['message']
    shared_secret = int(data['shared_secret'])
    encrypted_message = encrypt_message(message, shared_secret)

    # Store in AWS S3
    message_id = store_encrypted_message_s3(encrypted_message)

    return jsonify({"encrypted_message": encrypted_message, "message_id": message_id})


@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.form

    encrypted_message = data['encrypted_message']
    shared_secret = int(data['shared_secret'])
    decrypted_message = decrypt_message(encrypted_message, shared_secret)
    return jsonify({"decrypted_message": decrypted_message})


@app.route('/get_message_s3/<message_id>', methods=['GET'])
def get_message_s3(message_id):
    try:
        encrypted_message = retrieve_encrypted_message_s3(message_id)
        return jsonify({"message_id": message_id, "encrypted_message": encrypted_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/messages')
def messages():
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        messages = []
        if 'Contents' in response:
            for obj in response['Contents']:
                messages.append(obj['Key'].replace('.txt', ''))
        return render_template('messages.html', messages=messages)
    except Exception as e:
        return f"Error fetching messages: {e}"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

