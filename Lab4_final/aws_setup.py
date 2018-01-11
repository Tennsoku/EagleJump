import boto.ec2
import os
import sys
import time


def aws_initial():
	conn = boto.ec2.connect_to_region("us-east-1",aws_access_key_id='...',aws_secret_access_key='...')
	conn.delete_key_pair('mykey1')
	key = conn.create_key_pair('mykey1')				#Create key-pair
	os.system("rm -f mykey1.pem")
	key.save('./') 	#save key as .pem file

	test11 = conn.get_all_security_groups()
	print test11

	sec_group = conn.create_security_group('csc326-group31','csc326')	#create security group
	sec_group.authorize('ICMP',-1,-1,'0.0.0.0/0')
	
	sec_group.authorize('TCP',22,22,'0.0.0.0/0')
	
	sec_group.authorize('TCP',80,80,'0.0.0.0/0')
	

	rsv = conn.run_instances('ami-88aa1ce0', key_name='mykey1', instance_type='t1.micro',security_groups=['csc326-group31'])

	return (conn,rsv.instances[0])


def setup_static_ip_address(conn, instance):
	address = conn.allocate_address()
	address.associate(instance_id = instance.id)
	return address


def get_instance_status(conn, instance_ids=None):

	instances = conn.get_all_instance_status(instance_ids=instance_ids)
	print instances

	if not instances:
		return "none"
	else:
		return instances[0].system_status.status

def setup():

	conn, instance = aws_initial()

	while (get_instance_status(conn, instance_ids=instance.id) != 'ok'):
		time.sleep(1)

	address = setup_static_ip_address(conn, instance)

	print "aws finished"

	return (address.public_ip, instance.id, 'mykey1.pem')



