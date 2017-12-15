<html>
<body>
<form action="shorten.php" method="post">
URL to shorten: <input type="text" name="target" /><br>
<input type="submit" name="send" />
</form>
</body>
</html>
<?php
    $out = shell_exec( "/usr/bin/python3.6 /var/www/html/backend/shorten.py ".$_POST["target"]." ".$_SERVER["REMOTE_ADDR"] ) ;
    if(isset($_POST["send"])){
        echo "Your shortened URL is -- ".$out;
    }
?>
