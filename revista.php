DOI:
<form>
<input name="doi" type="text" />
</form>

<?php
  if ($_GET["doi"]){     
    $command = escapeshellcmd('./revista.py '.$_GET["doi"]);
    $output = shell_exec($command);
    echo $output;

  }
//phpinfo();
?>