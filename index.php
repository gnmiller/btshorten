<html>
<body>
<form action="index.php" method="post">
URL to shorten: <input type="text" name="target" /><br>
Specify String: <input type="text" name="manual" /><br>
<input type="submit" name="send" />
</form>
</body>
</html>
<?php
    $target = "";
    $manual = "";
    $py = "/usr/bin/python3.6";
    $shrt = "/var/www/html/backend/shorten.py";
    $str = $py . " " . $shrt . " '" . $_POST["target"] . "' '" . $_SERVER["REMOTE_ADDR"] . "'";
    $out = "";
    if( !empty($_POST["manual"]) && isset( $_POST["send"] ) ){
        $out = shell_exec( $str . " -m " . $_POST["manual"] );
    } elseif( isset( $_POST["send"] ) ){
        $out = shell_exec( $py . " " . $shrt . " '" . $_POST["target"] . "' '" . $_SERVER["REMOTE_ADDR"] . "'" );
    } elseif ( isset( $_POST["send"] ) ){
        echo "Error!";
    }
    if( isset( $_POST["send"] ) ){
        if( strpos($out,"ERR") != false ) {
           echo "Failed to create short URL!\n";
            echo $out;
        } else {
            echo "Your shortened URL is -- ".$out;
        }
    }
?>
