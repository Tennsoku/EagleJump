import sys
import os
import aws_setup

#sys.path.insert(0,'./csc326_lab3')
#sys.path.insert(0,'./csc326_lab3/frontend')


def developer():

	# aws instance setup
	public_ip, instance_id, key_pair_path = aws_setup.setup()

	# copy files to instance
	os.system("scp -r -o StrictHostKeyChecking=no -i %s ../lab4_final/ ubuntu@%s:~/" % (key_pair_path, public_ip))	

	# run enviroment setup in instance
	os.system("ssh -o StrictHostKeyChecking=no -i %s ubuntu@%s sudo nohup python lab4_final/pip_install.py" % (key_pair_path, public_ip))


	# all setup finish, print public id

	print "All setup finished, you can access the websit by following id:"
	print "public_id: %s" %public_ip
	print "instance_id: %s" %instance_id
	
	
developer()
