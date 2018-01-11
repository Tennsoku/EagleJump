import os
import sys

public_id="..."


os.system("scp -r -o StrictHostKeyChecking=no -i mykey1.pem ../lab4/ ubuntu@%s:~/" %public_id)	

os.system("ssh -o StrictHostKeyChecking=no -i mykey1.pem ubuntu@%s sudo nohup python lab4/pip_install.py" %public_id)

#os.system("ssh -o StrictHostKeyChecking=no -i mykey1.pem ubuntu@34.232.147.136 sudo nohup python lab4/csc326_lab3/frontend/HelloWorld.py")

	# all setup finish, print public id

print "All setup finished, you can access the websit by following id:"
print "public_id: %s" %public_id
	
