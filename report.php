<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Marshal Report</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css">
    <script src="//code.jquery.com/jquery-1.10.2.js"></script>
    <script src="//code.jquery.com/ui/1.11.4/jquery-ui.js"></script>

    <script type="text/javascript">
        var auto_refresh = setInterval(
            function(){
                $("#livetiming").load('livetiming.php');}, 1000);
    </script>
</head>

<body>

<div id="tabs">
    <ul>
        <li><a href="#livetiming">Live Timing</a></li>
        <li><a href="#raw">Raw</a></li>
    </ul>

    <div id="livetiming">
    </div>

    <div id="raw">
        <?php #print_r($data); ?>
    </div>
</div>

<script>
$("#tabs").tabs();
</script>

</body>
</html>
