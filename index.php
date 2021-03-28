<?php 
/*
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>
*/
?>

<!DOCTYPE html>
<?php

//Set your tally.xml-Location

$Tally_Config = '/opt/obs-tally-py/tally.xml';


/* You dont need to change anything below here */

if(isset($_POST['save']))
{
	$data=simplexml_load_file($Tally_Config);
	$data->host = $_POST['host'];
	$data->port = $_POST['port'];
  $data->pass = $_POST['pass'];
    
  $data->camera = $_POST['camera'];
    
	$data->p_red = $_POST['pRed'];
	$data->p_green = $_POST['pGreen'];
	$data->p_blue = $_POST['pBlue'];
    
	$handle = fopen($Tally_Config, "wb");
	fwrite($handle, $data->asXML());
	fclose($handle);
}

$data = simplexml_load_file($Tally_Config);
$host = $data->host;
$port = $data->port;
$pass = $data->pass;

$camera = $data->camera;

$pRed = $data->p_red;
$pGreen = $data->p_green;
$pBlue = $data->p_blue;

?>
<html>

<head>
  <style type='text/css'>
  /* form elements */
  label {
    display: block;
    padding: 3px 0;
  }

  legend {
    font-size: 1.1rem;
    padding: 7px;
    font-weight: 700;
  }

  fieldset {
    border-radius: 15px;
    margin-bottom: 10px;
  }

  body {
    background-color: #0c3871;
    color: #FFF;
    font-family: Verdana, Geneva, sans-serif;
  }

  input[type="text"] {
    padding: 6px 10px;
    border-radius: 5px;
    border: 1px solid #555;
  }

  input[type="submit"] {
    margin: 10px;
    padding: 10px 20px;
    border-radius: 9px;
    border: 2px solid #fff;
    background: none;
    font-size: 1rem;
    color: #fff;
    font-variant: all-small-caps;
    font-weight: 700;
  }

  input[type="submit"]:hover,
  input[type="submit"]:focus {
    background-color: #999;
    /* color: #999; */
    cursor: pointer;
  }

  button {
    background-color: inherit;
    border: inherit;
    cursor: pointer;
    color: #aaa;
    font-size: inherit;
    display: inline;
    text-decoration: underline;
  }
  </style>
  <title>OBS Tally Config</title>
</head>

<body>
  <form method="post">
    <div style='text-align:left;display:inline-block;width:100%;'>
      <div style='text-align:center;'>
        <noscript>To use OBSTally, please enable JavaScript<br /></noscript>
        <h1>OBS-Tally Config</h1>
        <p>Make your changes and press save once. The changes may take a few minutes to have an effect.</p>
      </div>
      <fieldset>
        <legend>OBS-Websocket Credentials</legend>
        <label for="host">Host:</label>
        <input type="text" cols="20" name="host" value="<?php echo $host; ?>" />
        <br />
        <label for="port">Port:</label>
        <input type="text" cols="20" name="port" value="<?php echo $port; ?>" />
        <br />
        <label for="pass">Pass:</label>
        <input type="text" cols="20" name="pass" placeholder="*********"></text"area>
        <br />
      </fieldset>

      <fieldset>
        <legend>OBS Camera/Source Name</legend>
        <p>
          If this name matches the name of a source in OBS, the light will turn yellow
          when the source is visible in preview and green if the source is visible in
          program.
        </p>
        <label for="camera">Source Name:</label>
        <input type="text" cols="20" name="camera" value="<?php echo $camera; ?>" />
        <br />
      </fieldset>

      <div style="padding: 10px 0;">
        <button onClick="return showHide();">RPi i/o options</button><span id="down" style="color: #aaa;">v</span><span
          id="up" style="display:none; color: #aaa;">^</span><br />
      </div>
      <fieldset id="gpio" style="display:none;">
        <legend>Define LED GPIOs as PI-GPIO-Numbers (NOT Pin-Number)</legend>
        <label for="pRed">Red Light GPIO:</label>
        <input type="text" cols="20" name="pRed" value="<?php echo $pRed; ?>" />
        <br />
        <label for="pGreen">Green Light GPIO:</label>
        <input type="text" cols="20" name="pGreen" value="<?php echo $pGreen; ?>" />
        <br />
        <label for="pBlue">Blue Light GPIO:</label>
        <input type="text" cols="20" name="pBlue" value="<?php echo $pBlue; ?>" />
        <br />
      </fieldset>
      <input type="submit" name="save" value="Save">
  </form>
</body>
<script type="text/javascript">
var show = false;
var el = document.getElementById("gpio");
var up = document.getElementById("up");
var down = document.getElementById("down");

function showHide() {
  show = !show;
  if (show) {
    el.style.display = 'block';
    up.style.display = 'inline';
    down.style.display = 'none';
  } else {
    el.style.display = 'none';
    up.style.display = 'none';
    down.style.display = 'inline';
  }
  return false;
}
</script>

</html>