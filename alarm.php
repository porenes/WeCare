<?
$tid = $_GET['tid'];
`sudo python /home/pi/scripts/alarm.py -t $tid >> /home/pi/scripts/log.txt`;

?>