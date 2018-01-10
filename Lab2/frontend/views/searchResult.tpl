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
    </head>

    <body>
		<!-- Navi bar -->
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

		
        <table id="results" class="wordCount">
            <p class="wordCount">Searching for "{{input}}" <br /></p>
			<tr><td><b> Word </b></td><td><b> Count </b></td></tr>
			%for word in words:
				%if word in unique_words:
					<tr><td>{{word}}</td>
					%count = words.count(word)
					<td> {{count}} </td><tr>
					%unique_words.remove(word)
				%end
			%end
		</table>


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

		<!-- History Table -->
        <div class="history">
			% if login == True:
				<b class="history"> Top Search </b>
				<table id="history" class="history">
				% if len(historyList) == 0:
				   <tr><td>No History Yet.</td></tr>
				% else:
				%   for topWord in historyList:
						<tr><td>{{topWord[0]}}</td>
						<td>{{topWord[1]}}</td></tr>
				% end
				</table>
			%end
        </div>

        <!-- RecentSearch -->
        <div class="recentSearch">
            % if login == True:
            <b> Recent Search </b>
            <table id="RecentSearch" class="RecentSearch">
                %   for input in recentSearch:
                <tr>
                    <td><i>{{input}}</i></td>
                </tr>
                % end
            </table>
            %end
        </div>

        <a href="/"><button>Back</button></a>
        
        

        <!-- Javascript -->
        <script language="Javascript" src="/static/assets/js/scripts.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/jquery-1.10.2.min.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/jquery.backstretch.min.js" type="text/javascript"> </script>
        <script language="Javascript" src="/static/assets/js/jquery.countdown.min.js" type="text/javascript"></script>
        <script language="Javascript" src="/static/assets/js/wow.min.js" type="text/javascript"></script>


    </body>

</html>
