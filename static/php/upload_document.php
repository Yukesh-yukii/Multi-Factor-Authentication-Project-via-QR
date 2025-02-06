<?php
// Database connection details
$servername = "localhost";
$username = "root";
$password = "Yukeshwaran@07";
$dbname = "aadhar_system";

// Connect to the database
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Target directory for file uploads
$targetDir = "uploads/";

// Check if the file is uploaded
if (isset($_FILES["file"]) && $_FILES["file"]["error"] == 0) {
    $fileName = basename($_FILES["file"]["name"]);
    $targetPath = $targetDir . $fileName;

    // Move the file to the target path
    if (move_uploaded_file($_FILES["file"]["tmp_name"], $targetPath)) {
        // Insert file details into the database
        $sql = "INSERT INTO files (filename, filepath) VALUES ('$fileName', '$targetPath')";
        if ($conn->query($sql) === TRUE) {
            echo "File uploaded and saved to the database successfully.";
        } else {
            echo "Error: " . $sql . " - " . $conn->error;
        }
    } else {
        echo "Error moving the file.";
    }
} else {
    echo "File not uploaded.";
}

// Close the database connection
$conn->close();
?>
