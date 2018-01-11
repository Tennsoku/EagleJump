import boto.ec2
import sys
import time


# variabel initializtion
conn = boto.ec2.connect_to_region("us-east-1",aws_access_key_id='...',aws_secret_access_key='...')

ip_address_list = conn.get_all_addresses()

# terminate the running istance
def terminate(instance_id):
	conn.terminate_instances(instance_id)
  
# find the running instance
def find_running_instance():
	i=True
	while (i):
		# get all instance
		instance_list = conn.get_only_instances()
		print instance_list
		if len(instance_list)==0:
			break;
		#find the running instance
		for e in instance_list:
			#print e.state
			if e.state == 'running' :
				instance_ids.append(e.id)
				ip_address.associate(e.id)				
				i = False
				break;
	return instance_ids

#check instance state
def get_instance_status(conn, instance_ids=None):

	instances = conn.get_only_instances()
	for i in instances:
		if i.state == 'shutting-down':
			return 'none' 
	
	return 'ok'
	


instance_ids = raw_input ("Please instance id to terminate it:")

terminate(instance_ids)
while (get_instance_status(conn, instance_ids) == 'none'):
	print "terminating the instance"
	time.sleep(1)
# delete security group
conn.delete_security_group ('csc326-group31')

print "security group csc326-group31 has been terminated"
print "instances "%s" has been terminated" %instance_ids






