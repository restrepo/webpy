<form>
Title:<br/>
<input name="title" type="text"><br/>
First author surname:<br/>
<input name="surname" type="text"><br/>
<input type="submit" value="Submit">
</form><br><br/>

<?php
  if ($_GET["surname"]){     
    $command = escapeshellcmd('./doi.py "'.$_GET["title"].'" "'.$_GET["surname"].'"');
    $output = shell_exec($command);
    echo $output;
  }
//phpinfo();
?>