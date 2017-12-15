<?php
echo "welcome!";
$out = shell_exec( "/usr/bin/python3.6 /root/workspace/btshorten/shorten.py gtb.com ".$_SERVER['REMOTE_ADDR'] );
echo $out;
?>
