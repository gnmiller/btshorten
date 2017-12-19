<html>
<body>
<form action="shorten.php" method="post">
URL to shorten: <input type="text" name="target" /><br>
Specify String: <input type="text" name="manual" /><br>
<input type="submit" name="send" />
</form>
</body>
</html>
<?php
    $py = "/usr/bin/python3.6";
    $shrt = "/var/www/html/backend/shorten.py";
    $str = $py . " " . $shrt . " '" . $_POST["target"] . "' '" . $_SERVER["REMOTE_ADDR"] . "'";
    $out = "";
    if( isset( $_POST["manual"] ) && isset( $_POST["send"] ) ){
        $out = shell_exec( $str . " -m " . $_POST["manual"] );
    } elseif( isset( $_POST["send"] ) ){
        $out = shell_exec( $py . " " . $shrt . " '" . $_POST["target"] . "' '" . $_SERVER["REMOTE_ADDR"] . "'" );
    } else {
        echo "Error!";
    }
    if( strpos($out,"ERR") != false ) {
        echo "Failed to create short URL!\n";
        echo $out;
    } else {
        echo "Your shortened URL is -- ".$out;
    }
?>
