<html>
    <head>

        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Eagle Jump!</title>

        <!-- CSS -->
        <link rel="stylesheet" href="/static/assets/bootstrap/bootstrap.min.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/animate.css" type="text/css">
		<link rel="stylesheet" href="/static/assets/css/form-elements.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/style.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/media-queries.css" type="text/css">


        <!-- Favicon -->
        <link rel="shortcut icon" href="/static/assets/ico/favicon.png">

        <!-- Javascript -->
        <script type="text/javascript" src="/static/assets/js/jquery-2.1.3.min.js"></script>

        <script language="Javascript" src="/static/assets/js/jquery.backstretch.min.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/scripts.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/wow.min.js" type="text/javascript"></script>
        
    </head>

    <body>
		<ul>
            <li><a class="active" a href="/">Home</a></li>
            % if login:
				<li style="float:right"><a class="Logout" href="/logout">Log out</a></li>
				<li style="float:right"><a class="Google" href={{link}}>Hello, {{name}}!</a></li>
				<li style="float:right"><img class="ProfileIco" src={{ico}} alt="Profile photo"></li>
            % else:
                <li style="float:right"><a class="Login" href="/login">Log in</a></li>
            % end
        </ul>

        <div>
            <img src="/static/assets/img/404.jpg" style="width:60%;height:60%;">
            </br>
            </br>
            </br>
        </div>

        <div>
            <a class="btn" style="font-size: 30px;background-color:#084E89;color: #fff;" href="/">Back to Home</a>
        </div>

		<!-- Footer -->
        <footer style="width: 100%">
	        <div class="container">
	            <div class="row" style="width: 100%">
	                <div class="col-sm-7 footer-copyright" style="width: 100%">
	                    <p>CSC326 Team 003<br>All rights reserved.</p>
	                </div>
	            </div>
	        </div>
        </footer>

    </body>

</html>
