<?php
/*
* Get latest version of the installer
*/

function get_latest_version(){
    $base_dir = "repo/amd64/builds/";
    $files = scandir($base_dir, SCANDIR_SORT_DESCENDING);
    $latest =  $base_dir . $files[0];
$format = <<<EOT
<a class="no-underline" href="$latest">Download</a>
EOT;
    return $format;
   
}

?>
