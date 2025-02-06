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

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $email = $_POST['email'];
    $aadhar = $_POST['aadhar'];
    $mobile = $_POST['mobile'];
    
    // Default password (change this later)
    $default_password = password_hash("defaultPassword123", PASSWORD_BCRYPT);

    // Basic validation
    if (!empty($username) && !empty($email) && !empty($aadhar) && !empty($mobile)) {
        // Insert the user data into the database with a default password
        $stmt = $conn->prepare("INSERT INTO users (username, email, aadhar, mobile, password_hash) VALUES (?, ?, ?, ?, ?)");
        $stmt->bind_param("sssss", $username, $email, $aadhar, $mobile, $default_password);

        if ($stmt->execute()) {
            // Redirect back to the admin panel after successful insertion
            header("Location: admin.php");
            exit();
        } else {
            echo "Error: " . $stmt->error;
        }
        $stmt->close();
    } else {
        echo "All fields are required.";
    }
}
$conn->close();
?>
