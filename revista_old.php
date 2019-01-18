DOI (and hit ENTER):
<form>
<input name="doi" type="text" />
</form>

<?php
  if ($_GET["doi"]){     
    $command = escapeshellcmd('./revista_old.py '.$_GET["doi"]);
    $output = shell_exec($command);
    echo $output;

  }
//phpinfo();
?>