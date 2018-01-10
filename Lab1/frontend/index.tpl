<html>
    <head>

        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Genesis</title>

        <!-- CSS -->
        <link rel="stylesheet" href="/static/assets/bootstrap/bootstrap.min.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/animate.css" type="text/css">
		<link rel="stylesheet" href="/static/assets/css/form-elements.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/style.css" type="text/css">
        <link rel="stylesheet" href="/static/assets/css/media-queries.css" type="text/css">

        <!-- Favicon and touch icons -->
        <link rel="shortcut icon" href="/static/assets/ico/favicon.png">
    </head>

    <body>

        <div class="coming-soon">
            <div class="inner-bg">
                <div class="container">
                    <div class="row">
                        <div class="col-sm-12">
                        	<div class="logo wow fadeInDown">
                        		<h1>
                                    <img src="/static/assets/img/logo.png">
                                    <p>Eagle Jump!</p>
                        		</h1>
                        	</div>
                            <div class="search wow fadeInUp">
			                    <form class="form-inline" action="" method="get">
			                        <input type="text" name="keywords" placeholder="Find your world!" class="search">
			                        <button type="submit" class="btn">Search!</button>
			                    </form>
			                    <div class="success-message"></div>
			                    <div class="error-message"></div>
			                </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="history">
            <p> Top Search </p>
            <table id="history" class="historyList">
            % if len(historyList) == 0:
               <p>No History Yet.</p>
            % else:
            %   for topWord in historyList:
                    <tr><td>{{topWord[0]}}</td>
                    <td>{{topWord[1]}}</td></tr>
            % end
            </table>
        </div>
        
        <!-- Footer -->
        <footer style="width: 100%">
	        <div class="container">
	            <div class="row" style="width: 100%">
	                <div class="col-sm-7 footer-copyright" style="width: 100%">
	                    <p>&copy; CSC326 Team G326-1-008<br>All rights reserved.</p>
	                </div>
	            </div>
	        </div>
        </footer>

        <!-- Javascript -->
        <script language="Javascript" src="/static/assets/js/scripts.js" type="text/javascript></script>
        <script language="Javascript" src="/static/assets/js/jquery-1.10.2.min.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/jquery.backstretch.min.js" type="text/javascript></script>
        <script language="Javascript" src="/static/assets/js/jquery.countdown.min.js" type="text/javascript></script>
        <script language="Javascript" src="/static/assets/js/wow.min.js" type="text/javascript></script>
        <script language="Javascript" src="/static/assets/js/scripts.js" type="text/javascript></script>


    </body>

</html>
