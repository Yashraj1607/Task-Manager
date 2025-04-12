from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = 'AC946b832c8f1e7b4b10f078185c56180f'
TWILIO_AUTH_TOKEN = 'a2cc59a8491d749305e7f8c8416395ef'
TWILIO_PHONE_NUMBER = '+19789158307'

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route('/')
def home():
    return r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task Manager</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: #f4f4f4;
                color: #333;
            }
            .container {
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background: #fff;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h2 {
                text-align: center;
                color: #444;
            }
            form label {
                font-weight: bold;
            }
            form input,
            form select {
                display: block;
                width: 100%;
                padding: 10px;
                margin: 10px 0;
            }
            form button {
                background: #28a745;
                color: #fff;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            form button:hover {
                background: #218838;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            table th,
            table td {
                padding: 10px;
                border: 1px solid #ccc;
            }
            table th {
                background: #f8f8f8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Task Manager</h2>
            <form id="taskForm">
                <label for="user-details">User Details:</label>
                <input type="text" id="user-details" placeholder="Enter user name or email" required>

                <label for="task-title">Task Title:</label>
                <input type="text" id="task-title" placeholder="Enter task title" required>

                <label for="from-date">From Date:</label>
                <input type="date" id="from-date" required>

                <label for="to-date">To Date:</label>
                <input type="date" id="to-date" required>

                <label for="status">Status:</label>
                <select id="status" required>
                    <option value="" disabled selected>Select Status</option>
                    <option value="In_Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                    <option value="Not_Completed">Not Completed</option>
                </select>

                <label for="mobile-number">Mobile Number:</label>
                <input type="text" id="mobile-number" placeholder="Enter mobile number (e.g., +919876543210)" required>

                <button type="submit">Add Task</button>
            </form>

            <h3>Task List</h3>
            <table>
                <thead>
                    <tr>
                        <th>Task ID</th>
                        <th>User Details</th>
                        <th>Title</th>
                        <th>Created Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="taskList"></tbody>
            </table>
        </div>
        <script>
            let taskIdCounter = 1;

            document.getElementById('taskForm').addEventListener('submit', function(event) {
                event.preventDefault();

                const userDetails = document.getElementById('user-details').value;
                const taskTitle = document.getElementById('task-title').value;
                const fromDate = document.getElementById('from-date').value;
                const toDate = document.getElementById('to-date').value;
                const status = document.getElementById('status').value;
                const mobileNumber = document.getElementById('mobile-number').value;

                // Validate mobile number in E.164 format
                if (!mobileNumber.match(/^\+\d{10,15}$/)) {
                    alert("Please enter a valid phone number in E.164 format (e.g., +919876543210).");
                    return;
                }

                const taskList = document.getElementById('taskList');
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${taskIdCounter}</td>
                    <td>${userDetails}</td>
                    <td>${taskTitle}</td>
                    <td>${new Date().toLocaleDateString()}</td>
                    <td>${status.charAt(0).toUpperCase() + status.slice(1)}</td>
                `;
                taskList.appendChild(row);

                if (status === "Not_Completed") {
                    sendTextMessage(mobileNumber, taskTitle, userDetails);
                }

                taskIdCounter++;
                this.reset();
            });

            function sendTextMessage(mobileNumber, taskTitle, userDetails) {
                const message = `Task "${taskTitle}" assigned to "${userDetails}" is not completed. Please take action!`;

                fetch('/send-sms', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phoneNumber: mobileNumber, message: message })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Message sent successfully!');
                        } else {
                            alert(`Failed to send message: ${data.error}`);
                        }
                    })
                    .catch(error => {
                        console.error('Error sending SMS:', error);
                        alert('An error occurred while sending the message.');
                    });
            }
        </script>
    </body>
    </html>
    '''


@app.route('/send-sms', methods=['POST'])
def send_sms():
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    message = data.get('message')

    try:
        # Validate phone number format
        if not phone_number.startswith('+') or not phone_number[1:].isdigit():
            raise ValueError("Phone number must be in E.164 format (e.g., +919876543210).")

        # Send SMS using Twilio
        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return jsonify({'success': True, 'sid': sms.sid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
