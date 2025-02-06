<?php
$servername = "localhost";
$username = "root";
$password = "Yukeshwaran@07";
$database = "secuqr_db";

// Create a connection
$conn = new mysqli($servername, $username, $password, $database);

// Check the connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Handle Delete User Request
if (isset($_GET['delete'])) {
    $id = intval($_GET['delete']);
    $conn->query("DELETE FROM users WHERE id=$id");
    header("Location: admin.php");
}

// Handle Update User Request
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['edit_id'])) {
    $id = intval($_POST['edit_id']);
    $aadhar = $_POST['aadhar'];
    $mobile = $_POST['mobile'];
    $conn->query("UPDATE users SET aadhar='$aadhar', mobile='$mobile' WHERE id=$id");
    header("Location: admin.php");
}

// Fetch users
$result = $conn->query("SELECT * FROM users");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #3498db, #8e44ad);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }

        .admin-container {
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 1000px;
            text-align: center;
        }

        h2 {
            color: #3498db;
            margin-bottom: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            padding: 12px;
            border: 1px solid #ddd;
            text-align: left;
        }

        th {
            background-color: #3498db;
            color: white;
        }

        input[type="text"] {
            padding: 8px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
        }

        button {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #2980b9;
        }

        .edit-button {
            background-color: #f39c12;
            color: white;
        }

        .delete-link {
            color: red;
            text-decoration: none;
            font-size: 14px;
        }

        .delete-link:hover {
            text-decoration: underline;
        }

        .add-user-button {
            margin-top: 20px;
            padding: 12px 20px;
            background-color: #2ecc71;
            color: white;
            font-size: 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .add-user-button:hover {
            background-color: #27ae60;
        }

        .add-user-form {
            margin-top: 20px;
            display: none;
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
        }

        .add-user-form input {
            width: 100%;
            margin: 10px 0;
            padding: 8px;
            font-size: 14px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
    <script>
        function enableEdit(id) {
            document.getElementById('aadhar_' + id).removeAttribute('readonly');
            document.getElementById('mobile_' + id).removeAttribute('readonly');
            document.getElementById('save_' + id).style.display = 'inline-block';
        }

        function toggleAddUserForm() {
            var form = document.getElementById('addUserForm');
            form.style.display = form.style.display === 'block' ? 'none' : 'block';
        }
    </script>
</head>
<body>
    <div class="admin-container">
        <h2>User Management</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Aadhar</th>
                <th>Mobile</th>
                <th>Actions</th>
            </tr>
            <?php while ($row = $result->fetch_assoc()) { ?>
            <tr>
                <td><?php echo $row['id']; ?></td>
                <td><?php echo $row['username']; ?></td>
                <td><?php echo $row['email']; ?></td>
                <td><input type="text" id="aadhar_<?php echo $row['id']; ?>" value="<?php echo $row['aadhar']; ?>" readonly></td>
                <td><input type="text" id="mobile_<?php echo $row['id']; ?>" value="<?php echo $row['mobile']; ?>" readonly></td>
                <td>
                    <button class="edit-button" onclick="enableEdit(<?php echo $row['id']; ?>)">Edit</button>
                    <form action="admin.php" method="POST" style="display:inline;">
                        <input type="hidden" name="edit_id" value="<?php echo $row['id']; ?>">
                        <input type="hidden" name="aadhar" id="hidden_aadhar_<?php echo $row['id']; ?>">
                        <input type="hidden" name="mobile" id="hidden_mobile_<?php echo $row['id']; ?>">
                        <button type="submit" id="save_<?php echo $row['id']; ?>" style="display:none;" onclick="
                            document.getElementById('hidden_aadhar_<?php echo $row['id']; ?>').value = document.getElementById('aadhar_<?php echo $row['id']; ?>').value;
                            document.getElementById('hidden_mobile_<?php echo $row['id']; ?>').value = document.getElementById('mobile_<?php echo $row['id']; ?>').value;
                        ">Save</button>
                    </form>
                    <a href="admin.php?delete=<?php echo $row['id']; ?>" class="delete-link" onclick="return confirm('Are you sure?')">Delete</a>
                </td>
            </tr>
            <?php } ?>
        </table>

        <button class="add-user-button" onclick="toggleAddUserForm()">Add User</button>
        
        <div id="addUserForm" class="add-user-form">
            <form action="add_user.php" method="POST">
                <input type="text" name="username" placeholder="Username" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="text" name="aadhar" placeholder="Aadhar" required>
                <input type="text" name="mobile" placeholder="Mobile" required>
                <button type="submit">Add</button>
            </form>
        </div>
    </div>
</body>
</html>
